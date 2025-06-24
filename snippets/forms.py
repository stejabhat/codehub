# snippets/forms.py

from django import forms
from .models import Snippet, Suggestion

class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['title', 'description', 'language', 'tags', 'code', 'code_file']

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ['new_code']
        widgets = {
            'new_code': forms.Textarea(attrs={'rows': 10, 'class': 'bg-white text-black w-full p-2 rounded'})
        }
