"""API serializers for portfolio."""
from rest_framework import serializers
from core.models import ContactMessage, CVDownload, Project, Experience, Skill


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for contact messages."""
    
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'message', 'created_at']
        read_only_fields = ['id', 'created_at', 'ip_address', 'user_agent']


class CVDownloadSerializer(serializers.ModelSerializer):
    """Serializer for CV download tracking."""
    
    class Meta:
        model = CVDownload
        fields = ['id', 'email', 'downloaded_at']
        read_only_fields = ['id', 'downloaded_at', 'ip_address', 'user_agent']


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for skills."""
    
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'proficiency', 'icon', 'is_featured']


class ExperienceSerializer(serializers.ModelSerializer):
    """Serializer for experience records."""
    end_date_display = serializers.ReadOnlyField()
    start_date_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Experience
        fields = [
            'id', 'company', 'role', 'start_date', 'end_date',
            'start_date_display', 'end_date_display', 'is_current',
            'description', 'technologies', 'order'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for projects."""
    technologies_list = serializers.SerializerMethodField()
    metrics_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'short_description', 'description',
            'image', 'category', 'technologies_list', 'metrics_list',
            'github_url', 'live_url', 'is_featured', 'created_at'
        ]
    
    def get_technologies_list(self, obj):
        return obj.get_technologies_list()
    
    def get_metrics_list(self, obj):
        return obj.get_metrics_list()


class ProjectDetailSerializer(ProjectSerializer):
    """Extended serializer for project detail view."""
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['updated_at']
