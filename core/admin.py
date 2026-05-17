from django.contrib import admin
from .models import SiteSettings, Testimonial, Client, SocialPost, StoreLocation, AnnouncementBar, SearchIndex
from .design_models import DesignSettings

from django.contrib import messages

@admin.register(StoreLocation)
class StoreLocationAdmin(admin.ModelAdmin):
    list_display = ('preview', 'name', 'city', 'phone', 'is_active', 'order')
    list_display_links = ('preview', 'name')
    list_editable = ('is_active', 'order')
    list_filter = ('city', 'is_active')
    search_fields = ('name', 'address', 'city')

    def preview(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{obj.get_image_url}" width="50" height="35" style="object-fit:cover; border-radius:4px; border:1px solid #ddd;" />')
    preview.short_description = "Image"
    
    fieldsets = (
        ('Location Info', {
            'fields': ('name', 'city', 'address', 'order'),
        }),
        ('Communication & Map', {
            'fields': ('phone', 'map_url'),
        }),
        ('Branding Image', {
            'fields': ('image', 'image_url', 'image_alt'),
        }),
    )
    radio_fields = {"is_active": admin.HORIZONTAL}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"🚀 Store Location '{obj.name}' has been successfully saved.")

    def delete_model(self, request, obj):
        name = obj.name
        super().delete_model(request, obj)
        messages.error(request, f"🗑️ Store Location '{name}' was deleted.")

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name',)
    fieldsets = (
        ('Overview & Branding', {
            'fields': ('site_name', 'company_name', 'fav_text', 'logo', 'logo_url', 'favicon', 'favicon_url'),
            'description': 'Main site identification and logo assets.'
        }),
        ('SEO Presence', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'google_site_verification_id', 'robots_txt', 'schema_markup'),
            'classes': ('collapse',),
        }),
        ('Tracking & Analytics', {
            'fields': ('google_analytics_id', 'facebook_pixel_id'),
            'classes': ('collapse',),
        }),
        ('Communication Channels', {
            'fields': ('email', 'phone', 'whatsapp'),
        }),
        ('Physical Presence', {
            'fields': ('branch1_name', 'dubai_address', 'branch2_name', 'abudhabi_address'),
        }),
        ('Footer & Notifications', {
            'fields': ('footer_quick_links_title', 'footer_support_title', 'footer_legal_title', 'footer_newsletter_title', 'footer_copyright_text', 'enable_email_notifications', 'enable_sms_notifications', 'enable_whatsapp_notifications'),
            'classes': ('collapse',),
        }),
        ('Social Links', {
            'fields': ('facebook', 'instagram', 'linkedin', 'twitter', 'instagram_handle'),
            'classes': ('collapse',),
        }),
    )
    radio_fields = {
        "enable_email_notifications": admin.HORIZONTAL,
        "enable_sms_notifications": admin.HORIZONTAL,
        "enable_whatsapp_notifications": admin.HORIZONTAL,
    }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, "⚙️ Global site settings have been successfully updated.")

@admin.register(DesignSettings)
class DesignSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'enable_glassmorphism', 'enable_ambient_glow', 'enable_animations')
    fieldsets = (
        ('Branding & Color Theme', {
            'fields': (
                'primary_color', 
                'secondary_color', 
                'accent_glow_color',
                'text_primary_color', 
                'text_secondary_color', 
                'text_white_color',
                'surface_bg_color', 
                'card_bg_color', 
                'border_color',
                'header_bg_color', 
                'header_text_color',
                'footer_bg_color', 
                'footer_text_color',
            ),
            'description': 'Master color palette for the entire storefront. Supports Hex codes (e.g., #114084).'
        }),
        ('Typography & Shapes', {
            'fields': (
                'font_main', 
                'font_secondary',
                'container_radius', 
                'card_radius',
                'button_radius', 
                'image_radius',
            ),
            'description': 'Select site-wide fonts and control the "softness" of the UI shapes.'
        }),
        ('Premium Effects', {
            'fields': (
                'enable_glassmorphism', 
                'enable_neumorphism', 
                'enable_ambient_glow', 
                'enable_animations', 
                'global_animation_type',
                'counter_animation_style', 
                'counter_animation_speed',
            ),
        }),
        ('Homepage Titles & Content', {
            'fields': (
                'hp_hero_title', 
                'hp_hero_subtitle',
                'hp_collections_title', 
                'hp_collections_subtitle',
                'hp_categories_title',
                'hp_latest_products_title', 
                'hp_latest_products_subtitle',
                'hp_partners_title', 
                'hp_services_title',
                'hp_gallery_title',
                'hp_testimonials_title',
                'hp_clients_title',
                'hp_social_title',
            ),
            'classes': ('collapse',),
            'description': 'Edit section headings and subheadings for the landing page.'
        }),
        ('App-Wide Page Titles', {
            'fields': (
                'cart_page_title', 
                'wishlist_page_title',
                'search_page_title', 
                'checkout_page_title',
                'profile_page_title', 
                'orders_page_title',
                'contact_page_title',
            ),
            'classes': ('collapse',),
            'description': 'Global control for all internal page headings.'
        }),
        ('Visibility & Display Controls', {
            'fields': (
                'show_header_search', 
                'show_header_wishlist', 
                'show_header_account', 
                'show_header_cart',
                'show_hp_categories', 
                'show_hp_latest_products', 
                'show_hp_brands',
                'show_hp_testimonials', 
                'show_hp_clients', 
                'show_hp_social',
                'pd_show_related', 
                'pd_related_title', 
                'pd_related_count',
            ),
            'description': 'Enable or disable major features and sections site-wide.'
        }),
    )
    radio_fields = {
        "enable_glassmorphism": admin.HORIZONTAL,
        "enable_neumorphism": admin.HORIZONTAL,
        "enable_ambient_glow": admin.HORIZONTAL,
        "enable_animations": admin.HORIZONTAL,
        "pd_show_related": admin.HORIZONTAL,
        "font_main": admin.HORIZONTAL,
        "font_secondary": admin.HORIZONTAL,
        # Visibility toggles
        "show_header_search": admin.HORIZONTAL,
        "show_header_wishlist": admin.HORIZONTAL,
        "show_header_account": admin.HORIZONTAL,
        "show_header_cart": admin.HORIZONTAL,
        "show_hp_categories": admin.HORIZONTAL,
        "show_hp_latest_products": admin.HORIZONTAL,
        "show_hp_brands": admin.HORIZONTAL,
        "show_hp_testimonials": admin.HORIZONTAL,
        "show_hp_clients": admin.HORIZONTAL,
        "show_hp_social": admin.HORIZONTAL,
    }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, "🎨 Design settings have been successfully updated.")

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('preview', 'client_name', 'position', 'rating', 'is_active', 'order')
    list_display_links = ('preview', 'client_name')
    list_editable = ('is_active', 'order')
    radio_fields = {"is_active": admin.HORIZONTAL}
    list_filter = ('rating', 'is_active')

    def preview(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{obj.get_image_url}" width="40" height="40" style="border-radius:50%; object-fit:cover; border:1px solid #ddd;" />')
    preview.short_description = "Photo"
    
    fieldsets = (
        ('Client Profile', {
            'fields': ('client_name', 'position', 'rating', 'order'),
        }),
        ('Content', {
            'fields': ('content',),
        }),
        ('Media', {
            'fields': ('image', 'image_url', 'image_alt'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"💬 Testimonial from '{obj.client_name}' has been saved.")

    def delete_model(self, request, obj):
        name = obj.client_name
        super().delete_model(request, obj)
        messages.error(request, f"🗑️ Testimonial from '{name}' was deleted.")

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('preview', 'name', 'category', 'is_active', 'order')
    list_display_links = ('preview', 'name')
    list_editable = ('category', 'is_active', 'order')
    radio_fields = {"is_active": admin.HORIZONTAL}
    list_filter = ('category', 'is_active')

    def preview(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{obj.get_image_url}" width="60" height="30" style="object-fit:contain; border:1px solid #eee; padding:2px; background:#fff; border-radius:4px;" />')
    preview.short_description = "Logo"
    
    fieldsets = (
        ('Client Info', {
            'fields': ('name', 'category', 'order'),
        }),
        ('Assets (Logo/Icon)', {
            'fields': ('logo', 'logo_url', 'image_alt', 'icon_svg'),
            'description': 'Provide either a traditional logo or a custom SVG path.'
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"🤝 Client '{obj.name}' has been successfully saved.")

    def delete_model(self, request, obj):
        name = obj.name
        super().delete_model(request, obj)
        messages.error(request, f"🗑️ Client '{name}' was removed.")

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('preview', 'link', 'order')
    list_display_links = ('preview', 'link')
    list_editable = ('order',)

    def preview(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{obj.get_image_url}" width="40" height="40" style="object-fit:cover; border-radius:4px; border:1px solid #ddd;" />')
    preview.short_description = "Preview"
    
    fieldsets = (
        ('Post Configuration', {
            'fields': ('link', 'order'),
        }),
        ('Media Assets', {
            'fields': ('image', 'image_url', 'image_alt', 'icon_svg'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, "📸 Social post entry has been saved.")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        messages.error(request, "🗑️ Social post entry was deleted.")

@admin.register(AnnouncementBar)
class AnnouncementBarAdmin(admin.ModelAdmin):
    list_display = ('text', 'start_date', 'end_date', 'closable', 'is_active')
    list_editable = ('is_active',)
    radio_fields = {"is_active": admin.HORIZONTAL, "closable": admin.HORIZONTAL}
    list_filter = ('is_active', 'closable')
    
    fieldsets = (
        ('Banner Message', {
            'fields': ('text', 'closable', 'is_active'),
        }),
        ('Appearance', {
            'fields': ('background_color', 'text_color'),
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date'),
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        messages.success(request, f"📢 Announcement '{obj.text[:30]}...' has been updated.")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        messages.error(request, "🗑️ Announcement was removed.")

