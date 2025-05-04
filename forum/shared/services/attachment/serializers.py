import os
import logging

from rest_framework import serializers
from .models import Attachments

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = ['id', 'file', 'file_type', 'created_at']
        read_only_fields = ['file_type', 'created_at']

    @staticmethod
    def validate_file(uploaded_file):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        logging.critical(f"validate_file in AttachmentSerializer - ext: {ext}")

        if ext not in Attachments.ALLOWED_IMAGE_EXT + Attachments.ALLOWED_TEXT_EXT:
            raise serializers.ValidationError("Недопустимый формат файла.")

        if ext in Attachments.ALLOWED_TEXT_EXT and uploaded_file.size > 100 * 1024:
            raise serializers.ValidationError("Размер текстового файла не должен превышать 100 КБ.")

        return uploaded_file
