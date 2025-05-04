from .events import *
from .tasks import log_event


def bind_event(signal, label):
    @signal.connect
    def handler(sender, **kwargs):
        print(f"[debug] signal triggered: {label}")
        kwargs.pop('signal', None)
        log_event.delay(label, kwargs)
    return handler


bind_event(comment_created, 'comment_created')
bind_event(reply_created, 'reply_created')
bind_event(xss_stripped, 'xss_stripped')
bind_event(captcha_failed, 'captcha_failed')
bind_event(invalid_attachment, 'invalid_attachment')
