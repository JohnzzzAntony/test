from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group, Permission

# ── MIXIN: User-Friendly Permissions ──────────────────────────────────────────

class UserFriendlyPermissionMixin:
    """Provides filtered, readable permission management for Users and Groups."""
    
    # Hide technical system apps to focus on business logic
    SYSTEM_APPS = ['admin', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'auth']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        try:
            if db_field.name in ["permissions", "user_permissions"]:
                # Filter the queryset to exclude internal system apps
                kwargs["queryset"] = Permission.objects.exclude(content_type__app_label__in=self.SYSTEM_APPS)
        except Exception:
            pass # Fallback to default if queryset filtering fails for any reason
            
        return super().formfield_for_manytomany(db_field, request, **kwargs)

# ── CUSTOM ADMINS ──────────────────────────────────────────────────────────────

# Wrapped in try-except to prevent startup crash if unregister/register order is tricky
try:
    admin.site.unregister(User)
except Exception:
    pass

@admin.register(User)
class UserAdmin(UserFriendlyPermissionMixin, BaseUserAdmin):
    """
    Refined User Management with high-readability permissions.
    """
    filter_horizontal = ('groups', 'user_permissions')

    class Media:
        css = {
            'all': ('admin/css/admin_offer.css',)
        }
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Safety check for 'groups' field which is often absent in 'Add User' forms or specific views
        if hasattr(form, 'base_fields') and 'groups' in form.base_fields:
            try:
                form.base_fields['groups'].widget.attrs['class'] = 'select2'
            except Exception:
                pass
        return form

try:
    admin.site.unregister(Group)
except Exception:
    pass

@admin.register(Group)
class GroupAdmin(UserFriendlyPermissionMixin, BaseGroupAdmin):
    """
    Refined Group Management with filtered permissions.
    """
    filter_horizontal = ('permissions',)

    class Media:
        css = {
            'all': ('admin/css/admin_offer.css',)
        }


from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)
