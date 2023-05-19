from typing import Any

from pydantic.utils import GetterDict

from app.models import PropertyPhoto


class PhotoGetter(GetterDict):
    def __init__(self, obj):
        self._is_default = getattr(obj, 'is_default', None)
        if isinstance(obj, PropertyPhoto):
            self._obj2 = obj.photo
        else:
            self._obj2 = obj
        super(PhotoGetter, self).__init__(obj)

    def get(self, key: Any, default: Any = None) -> Any:
        if hasattr(self._obj2, key):
            return getattr(self._obj2, key)
        return super(PhotoGetter, self).get(key, default)
