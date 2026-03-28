"""URL configuration for API app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContactMessageViewSet,
    CVDownloadView,
    ProjectViewSet,
    ExperienceViewSet,
    SkillViewSet,
    SiteConfigView,
    AnalyticsView,
)

router = DefaultRouter()
router.register(r'contact', ContactMessageViewSet, basename='contact')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'experience', ExperienceViewSet, basename='experience')
router.register(r'skills', SkillViewSet, basename='skill')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('cv-download/', CVDownloadView.as_view(), name='cv-download'),
    path('config/', SiteConfigView.as_view(), name='site-config'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]
