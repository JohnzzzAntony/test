from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('services/', views.services_view, name='services'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('store-locations/', views.store_locations_view, name='store_locations'),
    path('faq/', views.faq_view, name='faq'),
    path('shipping-info/', views.shipping_info_view, name='shipping_info'),
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions_view, name='terms_conditions'),
    path('health/', views.health_check, name='health_check'),
    path('robots.txt', views.robots_txt_view, name='robots_txt'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]
