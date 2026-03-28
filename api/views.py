"""API views for portfolio."""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django.conf import settings
import os

from core.models import ContactMessage, CVDownload, Project, Experience, Skill, SiteSettings
from .serializers import (
    ContactMessageSerializer,
    CVDownloadSerializer,
    ProjectSerializer,
    ExperienceSerializer,
    SkillSerializer,
)


class ContactRateThrottle(AnonRateThrottle):
    rate = '5/hour'


class ContactMessageViewSet(viewsets.ModelViewSet):
    """ViewSet for contact messages."""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ContactRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Add IP and user agent
        serializer.save(
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': 'Message sent successfully!'},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')


class CVDownloadView(APIView):
    """API view for CV download with tracking."""
    permission_classes = [AllowAny]

    def post(self, request):
        # Track download
        CVDownload.objects.create(
            email=request.data.get('email'),
            ip_address=self.get_client_ip(),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        # Get CV file
        site_settings = SiteSettings.objects.first()
        if not site_settings or not site_settings.cv_file:
            return Response(
                {'error': 'CV not available'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'url': site_settings.cv_file.url,
            'filename': os.path.basename(site_settings.cv_file.name)
        })

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return self.request.META.get('REMOTE_ADDR')


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for projects (read-only)."""
    queryset = Project.objects.filter(is_featured=True)
    serializer_class = ProjectSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = Project.objects.filter(is_featured=True)
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__icontains=category)
        return queryset


class ExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for experience (read-only)."""
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [AllowAny]


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for skills (read-only)."""
    queryset = Skill.objects.filter(is_featured=True)
    serializer_class = SkillSerializer
    permission_classes = [AllowAny]


class SiteConfigView(APIView):
    """API view for site configuration."""
    permission_classes = [AllowAny]

    def get(self, request):
        site_settings = SiteSettings.objects.first()
        if not site_settings:
            return Response({})

        return Response({
            'site_title': site_settings.site_title,
            'site_tagline': site_settings.site_tagline,
            'email': site_settings.email,
            'location': site_settings.location,
            'github_url': site_settings.github_url,
            'linkedin_url': site_settings.linkedin_url,
            'cv_available': bool(site_settings.cv_file),
        })


class AnalyticsView(APIView):
    """API view for analytics data (admin only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Basic analytics
        total_downloads = CVDownload.objects.count()
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()

        # Downloads by date (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_downloads = CVDownload.objects.filter(
            downloaded_at__gte=thirty_days_ago
        ).count()

        return Response({
            'total_cv_downloads': total_downloads,
            'total_messages': total_messages,
            'unread_messages': unread_messages,
            'recent_downloads_30d': recent_downloads,
        })
