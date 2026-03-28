"""Core application models for portfolio."""
from django.db import models
from django.utils import timezone


class ContactMessage(models.Model):
    """Model to store contact form submissions."""
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class CVDownload(models.Model):
    """Model to track CV downloads."""
    email = models.EmailField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-downloaded_at']

    def __str__(self):
        return f"CV Download by {self.email or 'Anonymous'} - {self.downloaded_at}"


class Skill(models.Model):
    """Model for technical skills."""
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('devops', 'DevOps & Cloud'),
        ('database', 'Database'),
        ('frontend', 'Frontend'),
        ('tools', 'Tools'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    proficiency = models.IntegerField(
        default=80,
        help_text="Proficiency level (0-100)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Material Icons class name"
    )
    order = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['category', 'order']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Experience(models.Model):
    """Model for professional experience timeline."""
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()
    technologies = models.TextField(
        help_text="Comma-separated list of technologies used"
    )
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['-start_date', '-order']

    def __str__(self):
        return f"{self.role} at {self.company}"

    @property
    def end_date_display(self):
        if self.is_current:
            return "Present"
        return self.end_date.strftime("%b %Y") if self.end_date else "Present"

    @property
    def start_date_display(self):
        return self.start_date.strftime("%Y")


class Project(models.Model):
    """Model for featured projects."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    category = models.CharField(max_length=100, default='Systems Design')
    technologies = models.TextField(
        help_text="Comma-separated list of technologies"
    )
    metrics = models.TextField(
        blank=True,
        help_text="Key achievements/metrics (one per line)"
    )
    github_url = models.URLField(blank=True, null=True)
    live_url = models.URLField(blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order', '-created_at']

    def __str__(self):
        return self.title

    def get_technologies_list(self):
        return [tech.strip() for tech in self.technologies.split(',')]

    def get_metrics_list(self):
        if not self.metrics:
            return []
        return [m.strip() for m in self.metrics.split('\n') if m.strip()]


class SiteSettings(models.Model):
    """Singleton model for site-wide settings."""
    site_title = models.CharField(
        max_length=255, default="GEORGE OGOLA // Architect v1.0")
    site_tagline = models.CharField(
        max_length=500,
        default="Building scalable systems that don't break at 3 AM."
    )
    cv_file = models.FileField(
        upload_to='cv/', help_text="Upload your CV file")
    github_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    email = models.EmailField(default="gogola89@gmail.com")
    location = models.CharField(max_length=255, default="Nairobi, Kenya")

    class Meta:
        verbose_name = 'Site Setting'

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError("SiteSettings singleton already exists!")
        return super().save(*args, **kwargs)
