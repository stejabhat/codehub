# snippets/forms.py

from django import forms
from .models import Snippet

class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['title', 'description', 'language', 'tags', 'code', 'code_file']
