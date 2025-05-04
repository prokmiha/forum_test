from django import forms
from django.urls import path
from django.http import JsonResponse
from django.contrib import admin
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from core.domains.comments.models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user_name", "email", "homepage", "text", "parent", "created_at", "main_thread"]
    search_fields = ["full_name", "phone"]

