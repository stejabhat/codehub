from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from pygments.lexers import guess_lexer
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from .models import (
    Snippet,
    Suggestion,
    Comment,
    Vote,
    Notification,
    SnippetVersion,
    Collection,
)
from .forms import SnippetForm, SuggestionForm, CommentForm


@login_required
def home(request):
    snippets = Snippet.objects.order_by("-date_created")
    query = request.GET.get("q")
    if query:
        snippets = snippets.filter(title__icontains=query) | snippets.filter(
            tags__icontains=query
        )

    # Split tags for each snippet
    for snippet in snippets:
        snippet.tag_list = [tag.strip() for tag in snippet.tags.split(",")]

    return render(request, "snippets/home.html", {"snippets": snippets})


@login_required
def snippet_detail(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    file_content = None
    highlighted_file = None
    highlighted_code = None

    if snippet.code_file:
        try:
            with snippet.code_file.open("r") as f:
                file_content = f.read()
                lexer = guess_lexer(file_content)
                formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
                highlighted_file = highlight(file_content, lexer, formatter)
        except Exception as e:
            file_content = f"Could not read file: {e}"

    if snippet.code and not highlighted_file:
        try:
            lexer = guess_lexer(snippet.code)
            formatter = HtmlFormatter(style="monokai", linenos=True, noclasses=True)
            highlighted_code = highlight(snippet.code, lexer, formatter)
        except Exception:
            highlighted_code = f"<pre>{snippet.code}</pre>"

    suggestions = snippet.suggestions.all()
    comments = snippet.comments.all().order_by("-created_at")

    upvotes = Vote.objects.filter(snippet=snippet, vote_type="up").count()
    downvotes = Vote.objects.filter(snippet=snippet, vote_type="down").count()
    score = upvotes - downvotes

    user_vote = None
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, snippet=snippet).first()

    comment_form = CommentForm()
    suggestion_form = SuggestionForm()

    return render(
        request,
        "snippets/detail.html",
        {
            "snippet": snippet,
            "file_content": file_content,
            "highlighted_file": highlighted_file,
            "highlighted_code": highlighted_code,
            "suggestions": suggestions,
            "comments": comments,
            "comment_form": comment_form,
            "suggestion_form": suggestion_form,
            "score": score,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "user_vote": user_vote,
        },
    )


@login_required
def snippet_upload(request):
    if request.method == "POST":
        form = SnippetForm(request.POST, request.FILES)
        if form.is_valid():
            snippet = form.save(commit=False)

            uploaded_file = request.FILES.get("code_file")
            if uploaded_file:
                snippet.code = uploaded_file.read().decode("utf-8")

            snippet.author = request.user
            snippet.save()
            return redirect("home")
    else:
        form = SnippetForm()
    return render(request, "snippets/upload.html", {"form": form})


@login_required
def snippet_delete(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    if request.user != snippet.author:
        return redirect("snippet_detail", pk=pk)
    if request.method == "POST":
        snippet.delete()
        return redirect("home")
    return render(request, "snippets/delete_confirm.html", {"snippet": snippet})


@login_required
def suggest_edit(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    # Prevent authors from suggesting edits to their own snippet
    if request.user == snippet.author:
        messages.warning(request, "You cannot suggest edits to your own snippet.")
        return redirect("snippet_detail", pk=pk)

    if request.method == "POST":
        form = SuggestionForm(request.POST)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.snippet = snippet
            suggestion.suggested_by = request.user
            suggestion.save()
            messages.success(request, "Your suggestion has been submitted!")
            return redirect("snippet_detail", pk=pk)
    else:
        form = SuggestionForm()

    return render(
        request, "snippets/suggest_edit.html", {"form": form, "snippet": snippet}
    )


@login_required
def snippet_edit(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.user != snippet.author:
        return redirect("snippet_detail", pk=pk)

    if request.method == "POST":
        form = SnippetForm(request.POST, request.FILES, instance=snippet)
        if form.is_valid():
            old_code = snippet.code
            old_title = snippet.title
            old_description = snippet.description
            old_language = snippet.language

            form.save()

            last_version = snippet.versions.first()
            new_version_number = (
                (last_version.version_number + 1) if last_version else 1
            )

            SnippetVersion.objects.create(
                snippet=snippet,
                code=old_code,
                title=old_title,
                description=old_description,
                language=old_language,
                version_number=new_version_number,
                changed_by=request.user,
            )

            return redirect("snippet_detail", pk=pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, "snippets/edit.html", {"form": form, "snippet": snippet})


@login_required
def version_history(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    versions = snippet.versions.all().order_by("-version_number")
    return render(
        request,
        "snippets/version_history.html",
        {"snippet": snippet, "versions": versions},
    )


@login_required
def revert_version(request, pk, version_id):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.user != snippet.author:
        return redirect("snippet_detail", pk=pk)

    version = get_object_or_404(SnippetVersion, pk=version_id, snippet=snippet)

    last_version = snippet.versions.first()
    new_version_number = (last_version.version_number + 1) if last_version else 1

    SnippetVersion.objects.create(
        snippet=snippet,
        code=snippet.code,
        title=snippet.title,
        description=snippet.description,
        language=snippet.language,
        version_number=new_version_number,
        changed_by=request.user,
    )

    snippet.code = version.code
    snippet.title = version.title
    snippet.description = version.description
    snippet.language = version.language
    snippet.save()

    messages.success(request, f"Reverted to version {version.version_number}")
    return redirect("snippet_detail", pk=pk)


@login_required
def fork_snippet(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    forked = Snippet.objects.create(
        title=f"{snippet.title} (Fork)",
        code=snippet.code,
        description=snippet.description,
        language=snippet.language,
        tags=snippet.tags,
        author=request.user,
    )

    messages.success(request, "Snippet forked! You can now edit your copy.")
    return redirect("snippet_detail", pk=forked.pk)


@login_required
def add_comment(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.snippet = snippet
            comment.author = request.user
            comment.save()

            if snippet.author and snippet.author != request.user:
                Notification.objects.create(
                    user=snippet.author,
                    notification_type="comment",
                    from_user=request.user,
                    snippet=snippet,
                    message=f"{request.user.username} commented on your snippet '{snippet.title}'",
                )

            messages.success(request, "Comment added!")
    return redirect("snippet_detail", pk=pk)


@login_required
def vote_snippet(request, pk):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    snippet = get_object_or_404(Snippet, pk=pk)
    vote_type = request.POST.get("vote_type")

    if vote_type not in ["up", "down"]:
        return JsonResponse({"error": "Invalid vote type"}, status=400)

    existing_vote = Vote.objects.filter(user=request.user, snippet=snippet).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete()
            vote_action = "removed"
        else:
            existing_vote.vote_type = vote_type
            existing_vote.save()
            vote_action = "changed"
    else:
        Vote.objects.create(user=request.user, snippet=snippet, vote_type=vote_type)
        vote_action = "added"

    upvotes = Vote.objects.filter(snippet=snippet, vote_type="up").count()
    downvotes = Vote.objects.filter(snippet=snippet, vote_type="down").count()
    score = upvotes - downvotes

    if vote_action == "added" and snippet.author and snippet.author != request.user:
        Notification.objects.create(
            user=snippet.author,
            notification_type="vote",
            from_user=request.user,
            snippet=snippet,
            message=f"{request.user.username} {'upvoted' if vote_type == 'up' else 'downvoted'} your snippet '{snippet.title}'",
        )

    return JsonResponse(
        {
            "score": score,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "action": vote_action,
        }
    )


@login_required
def notifications(request):
    user_notifications = request.user.notifications.filter(is_read=False).order_by(
        "-created_at"
    )
    return render(
        request, "snippets/notifications.html", {"notifications": user_notifications}
    )


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification, pk=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect("snippet_detail", pk=notification.snippet.pk)


@login_required
def collections(request):
    collections = request.user.collections.all()
    return render(request, "snippets/collections.html", {"collections": collections})


@login_required
def create_collection(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        is_public = request.POST.get("is_public", "on") == "on"

        collection = Collection.objects.create(
            name=name, description=description, owner=request.user, is_public=is_public
        )
        messages.success(request, f"Collection '{name}' created!")
        return redirect("collections")
    return render(request, "snippets/create_collection.html")


@login_required
def add_to_collection(request, collection_id, snippet_id):
    collection = get_object_or_404(Collection, pk=collection_id, owner=request.user)
    snippet = get_object_or_404(Snippet, pk=snippet_id)

    collection.snippets.add(snippet)
    messages.success(request, f"Added '{snippet.title}' to '{collection.name}'")
    return redirect("snippet_detail", pk=snippet_id)


@login_required
def remove_from_collection(request, collection_id, snippet_id):
    collection = get_object_or_404(Collection, pk=collection_id, owner=request.user)
    snippet = get_object_or_404(Snippet, pk=snippet_id)

    collection.snippets.remove(snippet)
    return redirect("collections")
