from app.models import enums


def order_accept_send_sms(language: enums.Languages, is_accept: bool = True):
    if is_accept:
        if language.UZ:
            text = 'some text when sending sms'
        elif language.RU:
            text = 'some text when sending sms'
        else:
            text = 'some text when sending sms'
    else:
        if language.UZ:
            text = 'some text when sending sms'
        elif language.RU:
            text = 'some text when sending sms'
        else:
            text = 'some text when sending sms'
    return text
