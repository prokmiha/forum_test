from django.dispatch import Signal


comment_created = Signal()
reply_created = Signal()
xss_stripped = Signal()
captcha_failed = Signal()
invalid_attachment = Signal()
