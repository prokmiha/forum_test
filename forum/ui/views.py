from django.shortcuts import render

from core.domains.comments.views import CommentsAPIView, CommentRepliesAPIView
from shared.services.attachment.views import AttachmentUploadAPIView
from shared.services.captcha.views import captcha_view



def base_comment_view(request):
    return render(request, "comment-system.html")

def comment_view(request, *args, **kwargs):
    view = CommentsAPIView.as_view()
    return view(request=request, *args, **kwargs)

def replies_view(request, *args, **kwargs):
    view = CommentRepliesAPIView.as_view()
    return view(request, *args, **kwargs)

def attachment_view(request, *args, **kwargs):
    view = AttachmentUploadAPIView.as_view()
    return view(request, *args, **kwargs)

def ui_captcha_view(request):
    return captcha_view(request=request)