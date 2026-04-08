from django.db import models
from django.contrib.auth.models import User


class Snippet(models.Model):
    title = models.CharField(max_length=200)
    code = models.TextField()
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50)
    tags = models.CharField(max_length=100, blank=True)
    code_file = models.FileField(upload_to="snippets/", blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


class Suggestion(models.Model):
    snippet = models.ForeignKey(
        Snippet, on_delete=models.CASCADE, related_name="suggestions"
    )
    suggested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    new_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suggestion by {self.suggested_by} on {self.snippet}"


class Comment(models.Model):
    snippet = models.ForeignKey(
        Snippet, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.snippet}"


class Vote(models.Model):
    VOTE_CHOICES = [
        ("up", "Upvote"),
        ("down", "Downvote"),
    ]
    snippet = models.ForeignKey(
        Snippet, on_delete=models.CASCADE, related_name="votes", null=True, blank=True
    )
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name="votes",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "snippet"],
                condition=models.Q(snippet__isnull=False),
                name="unique_user_snippet_vote",
            ),
            models.UniqueConstraint(
                fields=["user", "suggestion"],
                condition=models.Q(suggestion__isnull=False),
                name="unique_user_suggestion_vote",
            ),
        ]


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("comment", "New Comment"),
        ("suggestion", "New Suggestion"),
        ("vote", "New Vote"),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_notifications"
    )
    snippet = models.ForeignKey(
        Snippet, on_delete=models.CASCADE, null=True, blank=True
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type}: {self.message}"


class SnippetVersion(models.Model):
    snippet = models.ForeignKey(
        Snippet, on_delete=models.CASCADE, related_name="versions"
    )
    code = models.TextField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=50)
    version_number = models.IntegerField()
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"v{self.version_number} of {self.snippet.title}"


class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="collections"
    )
    snippets = models.ManyToManyField(Snippet, related_name="collections", blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
