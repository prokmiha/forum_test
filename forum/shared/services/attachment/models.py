import os

from django.db import models
from django.core.exceptions import ValidationError

from core.domains.comments.models import Comment

class Attachments(models.Model):
    TYPE_CHOICES = [
        ("image", 'Image'),
        ("text", 'Text file'),
    ]

    comment = models.ForeignKey(Comment, related_name="attachments", on_delete=models.CASCADE)
    file = models.FileField(upload_to="attachments/")
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        ext = os.path.splitext(self.file.name)[1].lower()
        allowed_ext_text = [".txt", ".doc"]
        allowed_ext_media = [".jpg", ".jpeg", ".png", ".gif"]
        allowed_ext = allowed_ext_media + allowed_ext_text

        if ext not in allowed_ext:
            raise ValidationError(f"Unsupported file extension: {ext}")
        
        if ext in allowed_ext_text:
            max_size = 100
            if self.file.size > max_size * 1024:
                raise ValidationError(f"Text file size exceeds {max_size}KB.")
            
            self.file_type = "text"
        else:
            self.file_type = "image"
        
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.file.name} ({self.file_type})"