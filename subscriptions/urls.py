from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='create_checkout'),
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('portal/', views.create_portal_session, name='portal'),
]
