from django.urls import path
from core.api_views import HeaderAPIView, DesignSettingsAPIView
from products.api_views import ProductSearchAPIView

urlpatterns = [
    path('header/', HeaderAPIView.as_view(), name='api-header'),
    path('search/', ProductSearchAPIView.as_view(), name='api-search'),
    path('design-settings/', DesignSettingsAPIView.as_view(), name='api-design-settings'),
]
