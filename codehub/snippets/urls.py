from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload/", views.snippet_upload, name="snippet_upload"),
    path("snippet/<int:pk>/", views.snippet_detail, name="snippet_detail"),
    path("snippet/<int:pk>/edit/", views.snippet_edit, name="snippet_edit"),
    path("snippet/<int:pk>/delete/", views.snippet_delete, name="snippet_delete"),
    path("snippet/<int:pk>/suggest/", views.suggest_edit, name="suggest_edit"),
    path("snippet/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("snippet/<int:pk>/vote/", views.vote_snippet, name="vote_snippet"),
    path("snippet/<int:pk>/fork/", views.fork_snippet, name="fork_snippet"),
    path("snippet/<int:pk>/versions/", views.version_history, name="version_history"),
    path(
        "snippet/<int:pk>/versions/<int:version_id>/revert/",
        views.revert_version,
        name="revert_version",
    ),
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read",
    ),
    path("collections/", views.collections, name="collections"),
    path("collections/create/", views.create_collection, name="create_collection"),
    path(
        "collections/<int:collection_id>/add/<int:snippet_id>/",
        views.add_to_collection,
        name="add_to_collection",
    ),
    path(
        "collections/<int:collection_id>/remove/<int:snippet_id>/",
        views.remove_from_collection,
        name="remove_from_collection",
    ),
]
