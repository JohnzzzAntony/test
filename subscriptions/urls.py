from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('pricing/', views.pricing_view, name='pricing'),
    path('checkout/<int:plan_id>/', views.create_checkout_session, name='create_checkout'),
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('portal/', views.create_portal_session, name='create_portal_session'),
    path('admin/metrics/', views.admin_subscription_metrics, name='admin_metrics'),
    path('admin/plans/', views.admin_subscription_plans, name='admin_plans'),
    path('admin/plans/create/', views.admin_edit_plan, name='admin_create_plan'),
    path('admin/plans/<int:plan_id>/edit/', views.admin_edit_plan, name='admin_edit_plan'),
    path('admin/plans/<int:plan_id>/delete/', views.admin_delete_plan, name='admin_delete_plan'),
]
