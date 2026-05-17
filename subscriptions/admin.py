from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'interval', 'is_active', 'stripe_price_id')
    list_filter = ('is_active', 'interval')
    search_fields = ('name', 'stripe_price_id')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_end')
    list_filter = ('status', 'plan')
    search_fields = ('user__username', 'stripe_customer_id', 'stripe_subscription_id')
    readonly_fields = ('stripe_customer_id', 'stripe_subscription_id')
