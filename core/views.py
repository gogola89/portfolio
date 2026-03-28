"""Views for core application."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import os

from .models import SiteSettings, Project, Experience, Skill, ContactMessage, CVDownload


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def home(request):
    """Home page view with all portfolio sections."""
    # Get site settings
    site_settings = SiteSettings.objects.first()
    
    # Get featured projects
    projects = Project.objects.filter(is_featured=True)[:4]
    
    # Get experience records
    experiences = Experience.objects.all()[:3]
    
    # Get skills by category
    skills = {
        'backend': Skill.objects.filter(category='backend', is_featured=True),
        'devops': Skill.objects.filter(category='devops', is_featured=True),
        'database': Skill.objects.filter(category='database', is_featured=True),
    }
    
    context = {
        'site_settings': site_settings,
        'projects': projects,
        'experiences': experiences,
        'skills': skills,
    }
    
    return render(request, 'core/home.html', context)


@require_http_methods(["GET", "POST"])
def cv_download(request):
    """Handle CV download with tracking."""
    site_settings = SiteSettings.objects.first()
    
    if not site_settings or not site_settings.cv_file:
        raise Http404("CV file not configured")
    
    # Track download
    CVDownload.objects.create(
        email=request.POST.get('email') if request.method == 'POST' else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Serve the file
    try:
        response = FileResponse(
            site_settings.cv_file.open(),
            as_attachment=True,
            filename=os.path.basename(site_settings.cv_file.name)
        )
        return response
    except FileNotFoundError:
        raise Http404("CV file not found")


def project_detail(request, slug):
    """Display individual project details."""
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'core/project_detail.html', {'project': project})


def error_404(request, exception):
    """Custom 404 error page."""
    return render(request, 'core/404.html', status=404)


def error_500(request):
    """Custom 500 error page."""
    return render(request, 'core/500.html', status=500)
