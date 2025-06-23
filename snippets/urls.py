from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('snippet/<int:pk>/', views.snippet_detail, name='snippet_detail'),
    path('upload/', views.snippet_upload, name='snippet_upload'),
    path('snippet/<int:pk>/delete/', views.snippet_delete, name='snippet_delete'),
    path('snippet/<int:pk>/edit/', views.snippet_edit, name='snippet_edit'),
    
]
