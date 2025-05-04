from django.db import models

class Comment(models.Model):
    user_name = models.CharField(max_length=64)
    email = models.EmailField()
    homepage = models.URLField(blank=True)
    text = models.TextField()
    parent = models.ForeignKey(to="self", null=True, blank=True, related_name="replies", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    main_thread = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_name} ({self.email})"
