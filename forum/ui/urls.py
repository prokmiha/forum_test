from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", RedirectView.as_view(url="comment/", permanent=False)),
    path("comment/", views.base_comment_view, name="comment"),

    path("api/comment/", views.comment_view, name="api-comment"),
    path("comment/<int:parent_id>/replies/", views.replies_view, name="comment-replies"),

    path("captcha/", views.ui_captcha_view, name="captcha"),
    path("api/attachment/", views.attachment_view, name="api-attachment"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
