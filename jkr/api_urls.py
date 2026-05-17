from django.urls import path
from core.api_views import HeaderAPIView
from products.api_views import ProductSearchAPIView

urlpatterns = [
    path('header/', HeaderAPIView.as_view(), name='api-header'),
    path('search/', ProductSearchAPIView.as_view(), name='api-search'),
]
