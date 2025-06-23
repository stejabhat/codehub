from django.db import models

from django.utils import timezone
# snippets/models.py

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from django.utils.safestring import mark_safe

class Snippet(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=30)
    code = models.TextField()
    code_file = models.FileField(upload_to='snippets/', blank=True, null=True)
    tags = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(default=timezone.now)  # ✅ Add this line
    def highlighted_code(self):
        try:
            lexer = get_lexer_by_name(self.language.lower(), stripall=True)
        except:
            lexer = get_lexer_by_name('text', stripall=True)

        formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
        return mark_safe(highlight(self.code, lexer, formatter))

    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

    def __str__(self):
        return self.title

