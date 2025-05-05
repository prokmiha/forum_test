from rest_framework import serializers
from django.conf import settings

from shared.services.events.tasks import send_comment_to_ws
from .models import Comment
from shared.services.attachment.models import Attachments


class AttachmentSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachments
        fields = ['id', 'file', 'file_type']

    def get_file(self, obj):
        if not obj.file:
            return None
        return f"{settings.MEDIA_URL}{obj.file.name}"


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    has_more_replies = serializers.SerializerMethodField()
    depth = serializers.SerializerMethodField()
    reply_count = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'email', 'homepage', 'text', 'parent', 'created_at', 'replies', 'has_more_replies', 'depth', 'reply_count', 'attachments']

    def create(self, validated_data):
        parent = validated_data.get("parent")
        if parent:
            validated_data["main_thread"] = parent.main_thread or parent.id

        instance = super().create(validated_data)
        send_comment_to_ws(CommentSerializer(instance).data)
        return instance

    def get_replies(self, obj):
        replies = obj.replies.order_by('-created_at')[:3]
        return ReplySerializer(replies, many=True).data

    def get_has_more_replies(self, obj):
        return obj.replies.count() > 3

    def get_depth(self, obj):
        if not obj.parent:
            return "reply-level-0"

        depth = 1
        current = obj
        while current.parent and current.parent_id != obj.main_thread:
            depth += 1
            current = current.parent

        return f"reply-level-{min(depth, 3)}"
    
    def get_reply_count(self, obj):
        return obj.replies.count()


class ReplySerializer(serializers.ModelSerializer):
    reply_count = serializers.SerializerMethodField()
    has_more_replies = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'email', 'homepage', 'text', 'parent', 'created_at', 'reply_count', 'has_more_replies', 'attachments']

    def create(self, validated_data):
        parent = validated_data.get("parent")
        if parent:
            validated_data["main_thread"] = parent.main_thread or parent.id

        instance = super().create(validated_data)
        send_comment_to_ws(CommentSerializer(instance).data)
        return instance

    def get_reply_count(self, obj):
        return obj.replies.count()

    def get_has_more_replies(self, obj):
        return obj.replies.count() > 3
