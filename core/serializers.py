from rest_framework import serializers
from .models import AnnouncementBar, SiteSettings
from .design_models import DesignSettings

class AnnouncementBarSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementBar
        fields = '__all__'

class SiteSettingsSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = SiteSettings
        fields = ('site_name', 'company_name', 'logo_url', 'phone', 'email', 'whatsapp', 'facebook', 'instagram', 'linkedin', 'twitter')

    def get_logo_url(self, obj):
        return obj.get_logo_url()

class DesignSettingsSerializer(serializers.ModelSerializer):
    """Serializer for real-time theme preview - exposes all design tokens"""
    class Meta:
        model = DesignSettings
        fields = '__all__'
