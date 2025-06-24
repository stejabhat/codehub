from django.shortcuts import render, redirect, get_object_or_404
from .models import Snippet
from .forms import SnippetForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from pygments.lexers import guess_lexer
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Snippet
from .forms import SuggestionForm
from django.contrib import messages
@login_required
def home(request):
    snippets = Snippet.objects.order_by('-date_created')
    query = request.GET.get('q')
    if query:
        snippets = snippets.filter(title__icontains=query) | snippets.filter(tags__icontains=query)
    
    # Split tags for each snippet
    for snippet in snippets:
        snippet.tag_list = [tag.strip() for tag in snippet.tags.split(',')]
    
    return render(request, 'snippets/home.html', {'snippets': snippets})

@login_required
def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    file_content = None
    highlighted_file = None
    highlighted_code = None

    # Highlighting logic (no change)
    if snippet.code_file:
        try:
            with snippet.code_file.open('r') as f:
                file_content = f.read()
                lexer = guess_lexer(file_content)
                formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
                highlighted_file = highlight(file_content, lexer, formatter)
        except Exception as e:
            file_content = f"⚠️ Could not read file: {e}"

    if snippet.code and not highlighted_file:
        try:
            lexer = guess_lexer(snippet.code)
            formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
            highlighted_code = highlight(snippet.code, lexer, formatter)
        except Exception:
            highlighted_code = f"<pre>{snippet.code}</pre>"

    # ✅ Get suggestions for this snippet
    suggestions = snippet.suggestions.all()

    return render(request, 'snippets/detail.html', {
        'snippet': snippet,
        'file_content': file_content,
        'highlighted_file': highlighted_file,
        'highlighted_code': highlighted_code,
        'suggestions': suggestions,  # ✅ Send to template
    })
def snippet_upload(request):
    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)

            uploaded_file = request.FILES.get('code_file')
            if uploaded_file:
                snippet.code = uploaded_file.read().decode('utf-8')  # 👈 autofill

            snippet.save()
            return redirect('home')
    else:
        form = SnippetForm()
    return render(request, 'snippets/upload.html', {'form': form})

def snippet_delete(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    if request.method == 'POST':
        snippet.delete()
        return redirect('home')
    return render(request, 'snippets/delete_confirm.html', {'snippet': snippet})



@login_required
def suggest_edit(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    # Prevent authors from suggesting edits to their own snippet
    if request.user == snippet.author:
        messages.warning(request, "You cannot suggest edits to your own snippet.")
        return redirect('snippet_detail', pk=pk)

    if request.method == "POST":
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.snippet = snippet
            suggestion.suggested_by = request.user
            suggestion.save()
            messages.success(request, "Your suggestion has been submitted!")
            return redirect('snippet_detail', pk=pk)
    else:
        form = SuggestionForm()

    return render(request, 'snippets/suggest_edit.html', {'form': form, 'snippet': snippet})
@login_required
def suggest_edit_view(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    form = SuggestionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        suggestion = form.save(commit=False)
        suggestion.snippet = snippet
        suggestion.suggested_by = request.user
        suggestion.save()
        return redirect('snippet_detail', pk=snippet.pk)

    return render(request, 'snippets/suggest_edit.html', {'form': form, 'snippet': snippet})

@login_required
def snippet_edit(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.user != snippet.author:
        return redirect('snippet_detail', pk=pk)

    if request.method == 'POST':
        form = SnippetForm(request.POST, request.FILES, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', pk=pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, 'snippets/edit.html', {'form': form, 'snippet': snippet})
