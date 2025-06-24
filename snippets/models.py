from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Snippet(models.Model):
    title = models.CharField(max_length=200)
    code = models.TextField()
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    tags = models.CharField(max_length=100, blank=True)
    code_file = models.FileField(upload_to='snippets/', blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)  # ✅ Add this line
    def __str__(self):
        return self.title

class Suggestion(models.Model):
    snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name="suggestions")
    suggested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    new_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suggestion by {self.suggested_by} on {self.snippet}"
