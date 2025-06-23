from django.db import models

from django.utils import timezone

class Snippet(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=30)
    code = models.TextField()
    tags = models.CharField(max_length=100, blank=True)
    code_file = models.FileField(upload_to='snippets/', blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)  # ✅ Add this line

    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def __str__(self):
        return self.title
