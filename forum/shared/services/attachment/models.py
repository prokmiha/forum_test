import os
from django.db import models
from django.core.exceptions import ValidationError
from core.domains.comments.models import Comment
from PIL import Image

class Attachments(models.Model):
    FILE_TYPE_IMAGE = 'image'
    FILE_TYPE_TEXT = 'text'

    ALLOWED_IMAGE_EXT = ['.jpg', '.jpeg', '.png', '.gif']
    ALLOWED_TEXT_EXT = ['.txt']

    TYPE_CHOICES = [
        (FILE_TYPE_IMAGE, 'Image'),
        (FILE_TYPE_TEXT, 'Text file'),
    ]

    comment = models.ForeignKey(Comment, related_name="attachments", on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="")
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        ext = os.path.splitext(self.file.name)[1].lower()

        if ext not in self.ALLOWED_IMAGE_EXT + self.ALLOWED_TEXT_EXT:
            raise ValidationError(f"Unsupported file extension: {ext}")

        if ext in self.ALLOWED_TEXT_EXT:
            if self.file.size > 100 * 1024:
                raise ValidationError("Text file size must be ≤ 100KB.")
            self.file_type = self.FILE_TYPE_TEXT

        elif ext in self.ALLOWED_IMAGE_EXT:
            self.file_type = self.FILE_TYPE_IMAGE
            self._resize_image()

    def _resize_image(self):
        try:
            img = Image.open(self.file)
            if img.width > 320 or img.height > 240:
                img.thumbnail((320, 240))
                img_format = img.format or 'JPEG'

                from io import BytesIO
                buffer = BytesIO()
                img.save(buffer, format=img_format)
                buffer.seek(0)

                from django.core.files.uploadedfile import InMemoryUploadedFile
                self.file = InMemoryUploadedFile(
                    buffer, 'ImageField', self.file.name, f'image/{img_format.lower()}',
                    buffer.getbuffer().nbytes, None
                )
        except Exception:
            raise ValidationError("Ошибка при обработке изображения.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"
