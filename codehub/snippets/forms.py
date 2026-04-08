# snippets/forms.py

from django import forms
from .models import Snippet, Suggestion, Comment


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ["title", "description", "language", "tags", "code", "code_file"]


class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = ["new_code"]
        widgets = {
            "new_code": forms.Textarea(
                attrs={"rows": 10, "class": "bg-white text-black w-full p-2 rounded"}
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full bg-gray-900 text-white border border-gray-700 rounded p-2",
                    "placeholder": "Add a comment...",
                }
            )
        }
