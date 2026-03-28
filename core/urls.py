"""URL configuration for core app."""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('cv/download/', views.cv_download, name='cv_download'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
]
