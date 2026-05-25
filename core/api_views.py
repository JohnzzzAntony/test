from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import AnnouncementBar, SiteSettings
from .design_models import DesignSettings
from products.models import Category
from .serializers import AnnouncementBarSerializer, SiteSettingsSerializer, DesignSettingsSerializer
from products.serializers import CategorySerializer

class HeaderAPIView(APIView):
    def get(self, request):
        now = timezone.now()
        # Get active announcement
        announcement = AnnouncementBar.objects.filter(
            is_active=True
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=now)
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        ).first()

        site_settings = SiteSettings.objects.first()
        # Top-level categories only
        categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('homepage_order', 'name')

        return Response({
            'announcement': AnnouncementBarSerializer(announcement).data if announcement else None,
            'settings': SiteSettingsSerializer(site_settings).data if site_settings else None,
            'categories': CategorySerializer(categories, many=True).data
        })

class DesignSettingsAPIView(APIView):
    """
    API endpoint for real-time theme preview.
    Returns all DesignSettings as CSS custom properties for live preview.
    """
    def get(self, request):
        design = DesignSettings.objects.first()
        if not design:
            design = DesignSettings.objects.create(id=1)
        
        serializer = DesignSettingsSerializer(design)
        return Response(serializer.data)
    
    def patch(self, request):
        """Partial update for live preview - doesn't persist to database"""
        design = DesignSettings.objects.first()
        if not design:
            design = DesignSettings.objects.create(id=1)
        
        # Return the proposed changes as CSS variables without saving
        return Response({
            'preview': True,
            'changes': request.data,
            'css_variables': self._generate_css_variables(request.data)
        })
    
    def _generate_css_variables(self, data):
        """Convert settings data to CSS custom properties"""
        css_vars = {}
        color_fields = [
            'primary_color', 'secondary_color', 'accent_color', 'accent_hover_color',
            'text_primary_color', 'text_secondary_color', 'text_white_color', 'text_accent_color',
            'surface_bg_color', 'card_bg_color', 'border_color', 'border_hover_color',
            'header_bg_color', 'header_text_color', 'header_border_color',
            'footer_bg_color', 'footer_text_color', 'footer_heading_color',
            'category_bg_color', 'price_color', 'sale_price_color', 'rating_star_color',
            'button_primary_bg', 'button_primary_text', 'button_primary_hover_bg',
            'button_secondary_bg', 'button_secondary_text', 'button_secondary_border',
            'button_secondary_hover_bg', 'button_secondary_hover_text',
        ]
        
        for field in color_fields:
            if field in data:
                css_vars[f'--{field}'] = data[field]
        
        # Typography
        if 'font_main' in data:
            css_vars['--font-main'] = data['font_main']
        if 'font_heading' in data:
            css_vars['--font-heading'] = data['font_heading']
        if 'font_accent' in data:
            css_vars['--font-accent'] = data['font_accent']
        
        # Spacing & Radius
        if 'container_radius' in data:
            css_vars['--radius-container'] = data['container_radius']
        if 'card_radius' in data:
            css_vars['--radius-card'] = data['card_radius']
        if 'button_radius' in data:
            css_vars['--radius-btn'] = data['button_radius']
        if 'image_radius' in data:
            css_vars['--radius-img'] = data['image_radius']
        if 'spacing_unit' in data:
            css_vars['--space-unit'] = f"{data['spacing_unit']}px"
        if 'section_padding' in data:
            css_vars['--section-padding'] = f"{data['section_padding']}px"
        if 'container_padding' in data:
            css_vars['--container-padding'] = f"{data['container_padding']}px"
        
        return css_vars
