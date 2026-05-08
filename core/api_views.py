from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ai_services import KimiAIService

from django.utils import timezone
from .models import AnnouncementBar, SiteSettings
from products.models import Category
from .serializers import AnnouncementBarSerializer, SiteSettingsSerializer
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

class KimiChatAPIView(APIView):
    """
    API endpoint to chat with Kimi AI.
    """
    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        system_prompt = request.data.get('system_prompt', 'You are a helpful assistant.')
        
        try:
            service = KimiAIService()
            # result is a ChatCompletion object
            completion = service.chat(prompt, system_prompt=system_prompt, stream=False)
            return Response({
                'content': completion.choices[0].message.content,
                'reasoning': getattr(completion.choices[0].message, 'reasoning_content', None)
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

