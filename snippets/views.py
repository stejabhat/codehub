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


def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    file_content = None
    highlighted_file = None

    if snippet.code_file:
        try:
            with snippet.code_file.open('r') as f:
                file_content = f.read()
                lexer = guess_lexer(file_content)
                formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
                highlighted_file = highlight(file_content, lexer, formatter)
        except Exception as e:
            file_content = f"⚠️ Could not read file: {e}"

    return render(request, 'snippets/detail.html', {
        'snippet': snippet,
        'file_content': file_content,
        'highlighted_file': highlighted_file,
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

def snippet_edit(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('snippet_detail', pk=pk)
    else:
        form = SnippetForm(instance=snippet)
    return render(request, 'snippets/edit.html', {'form': form, 'snippet': snippet})

