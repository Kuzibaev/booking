import functools
import hashlib
import inspect
import re
from typing import Callable

from fastapi import Request

from app.core.conf import settings
from app.core.sessions import redis


class RateLimitExceeded(Exception):
    def __init__(self, time_left: int):
        super(RateLimitExceeded, self).__init__()
        self.time_left = time_left


_PERIODS = {
    's': 1,
    'm': 60,
    'h': 60 * 60,
    'd': 24 * 60 * 60,
}
rate_re = re.compile(r'([\d]+)/([\d]*)([smhd])?')  # noqa


def _split_rate(rate):
    if isinstance(rate, tuple):
        return rate
    count, multi, period = rate_re.match(rate).groups()
    count = int(count)
    if not period:
        period = 's'
    seconds = _PERIODS[period.lower()]
    if multi:
        seconds = seconds * int(multi)
    return count, seconds


async def _get_key_value(key, request, **kwargs):
    if callable(key):
        _kwargs = {}
        spec = inspect.getfullargspec(key)
        for arg in spec.args:
            arg_ann = spec.annotations.get(arg, None)
            if arg_ann == Request or arg == "request":
                _kwargs[arg] = request
            elif arg in kwargs:
                _kwargs[arg] = kwargs[arg]
            else:
                _kwargs[arg] = None
        if inspect.iscoroutinefunction(key):
            value = await key(**_kwargs)
        else:
            value = key(**_kwargs)
        if not value:
            raise ValueError('Ratelimit key returned None value')
    else:
        value = key
    try:
        value = str(value)
    except ValueError:
        raise ValueError("Ratelimit key returned non string value")
    else:
        return value


def _add_request_to_signature(fn):
    signature = inspect.signature(fn)
    for param in signature.parameters:
        if signature.parameters[param].annotation == Request:
            return False
    return signature.replace(parameters=[
        inspect.Parameter(
            name='request',
            kind=inspect.Parameter.POSITIONAL_ONLY,
            annotation=Request
        ),
        *signature.parameters.values(),
    ])


def _find_request_obj(kwargs: dict, pop: bool):
    _kwargs = {}
    req = None
    for k, v in kwargs.items():
        if isinstance(v, Request):
            req = v
            if not pop:
                _kwargs[k] = v
        else:
            _kwargs[k] = v
    return req, _kwargs


def rate_limit(key: Callable, rate: str, raise_exception: bool = True):
    def decorator(fn):
        signature = _add_request_to_signature(fn)

        @functools.wraps(fn)
        async def _wrapped(**kwargs):
            request, kwargs = _find_request_obj(kwargs, bool(signature))
            value = await _get_key_value(key, request, **kwargs)
            is_limited, retry_after = await _is_limited(value, rate, fn, method=request.method)
            if is_limited:
                if raise_exception:
                    raise RateLimitExceeded(time_left=retry_after)
                else:
                    request.state.is_limited = is_limited
                    request.state.retry_after = retry_after
            if inspect.iscoroutinefunction(fn):
                response = await fn(**kwargs)
            else:
                response = fn(**kwargs)
            return response

        if signature:
            _wrapped.__signature__ = signature
        return _wrapped

    return decorator


async def _is_limited(value: str, rate: str, fn: Callable, method: str):
    parts = []
    if isinstance(fn, functools.partial):
        fn = fn.func

    if hasattr(fn, '__module__'):
        parts.append(fn.__module__)

    if hasattr(fn, '__self__'):
        parts.append(fn.__self__.__class__.__name__)
    parts.append(fn.__qualname__)
    group = '.'.join(parts)
    limit, period = _split_rate(rate)
    if period <= 0:
        raise ValueError("Ratelimit period must be greater than 0")
    _cache_key = _make_cache_key(group, rate, value, method)
    usage = int((await redis.get(_cache_key)) or 0)
    if not usage:
        await redis.set(_cache_key, 1, ex=period)
    elif usage >= limit:
        expire_after_seconds = await redis.ttl(_cache_key)
        return True, expire_after_seconds
    else:
        await redis.incr(_cache_key, 1)
    return False, 0


def _make_cache_key(group, rate, value, method):
    prefix = getattr(settings, 'RATE_LIMIT_PREFIX', 'app:rl:')
    count, period = _split_rate(rate)
    safe_rate = '%d/%ds' % (count, period)
    parts = [group, safe_rate, value, method]
    _cache_key = prefix + hashlib.md5(u''.join(parts).encode('utf-8')).hexdigest()
    return _cache_key
