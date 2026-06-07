from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Product, ProductImage, Offer, Collection, Wishlist, Brand, TrustBadge
from .forms import ProductAdminForm
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .resources import CategoryResource, ProductResource

# ─── Inlines ─────────────────────────────────────────────────────────────────

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'image_alt', 'order')
    show_change_link = False   # removes the "Original" pk column entirely
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images"


class SubCategoryInline(admin.TabularInline):
    model = Category
    fk_name = 'parent'
    extra = 0
    verbose_name = "Sub Category"
    verbose_name_plural = "Sub Categories"
    fields = ('name', 'slug', 'show_on_homepage', 'homepage_order')
    prepopulated_fields = {"slug": ("name",)}

# ─── Main Model Admins ───────────────────────────────────────────────────────

@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    form = ProductAdminForm
    resource_class = ProductResource
    list_display = ('name', 'category_display', 'brand', 'regular_price', 'sale_price', 'quantity', 'exclusive_products', 'on_sale_now', 'stock_status', 'preview')
    list_editable = ('on_sale_now', 'brand', 'exclusive_products')
    search_fields = ('name', 'slug', 'sku_id', 'brand__name')
    list_filter = ('brand', 'category', 'exclusive_products', 'on_sale_now', 'is_active')
    readonly_fields = ('sku_id', 'preview', 'badge_management')
    inlines = [ProductImageInline]
    # change_list_template = "admin/products/product/change_list.html"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'category__parent', 'brand')

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('download-demo-excel/', self.admin_site.admin_view(self.download_demo_excel), name='product-demo-excel'),
            path('download-demo-csv/', self.admin_site.admin_view(self.download_demo_csv), name='product-demo-csv'),
        ]
        return custom_urls + urls

    def _get_demo_dataset(self):
        import tablib
        resource = self.resource_class()
        
        # Get actual headers from the resource
        headers = resource.get_export_headers()
        dataset = tablib.Dataset(headers=headers)
        
        # Mapping values to headers to avoid index confusion
        # Fields: id, category, name, slug, image, image_url, sku_id, quantity, unit, 
        # regular_price, sale_price, shipping_status, free_shipping, 
        # additional_shipping_charge, delivery_time, tax_percentage, 
        # weight, length, width, height, features, overview, technical_info, 
        # created_at, show_on_homepage, is_active, meta_title, meta_description, meta_keywords
        
        sample_row_1 = [
            "", # id
            "Medical Equipment", # category
            "Brand Name", # brand
            "Sample Premium Stethoscope", # name
            "sample-premium-stethoscope", # slug
            "", # image field (physical path)
            "https://res.cloudinary.com/demo/image/upload/sample.jpg", # image_url
            "MED-STETH-001", # sku_id
            10, # quantity
            "pcs", # unit
            550.00, # regular_price
            495.00, # sale_price
            "available", # shipping_status
            True, # free_shipping
            0.00, # additional_shipping_charge
            "2-3 business days", # delivery_time
            5.00, # tax_percentage
            0.5, # weight
            30.0, # length
            15.0, # width
            5.0, # height
            "Professional grade stethoscope for cardiologists.", # features
            "<p>Superb acoustics; Dual-lumen tubing; Stainless steel chestpiece.</p>", # overview
            "<p>Weight: 150g; Length: 69cm.</p>", # technical_info
            "<p>Free returns within 14 days.</p>", # shipping_returns
            4.8, # avg_rating
            120, # review_count
            "NEW", # badge
            "blue", # badge_color
            True, # exclusive_products
            True, # on_sale_now
            True, # is_active
            "2024-01-01 10:00:00", # created_at
            "Best Stethoscope UAE", # meta_title
            "Buy the best medical stethoscope in Dubai with fast delivery.", # meta_description
            "stethoscope, medical, cardiology, uae", # meta_keywords
            "", # gallery_image_urls
            "", # category_image_url
        ]
        
        sample_row_2 = [
            "", # id
            "Medical Consumables", # category
            "HealthBrand", # brand
            "Digital Blood Pressure Monitor", # name
            "digital-bp-monitor", # slug
            "", # image field
            "https://res.cloudinary.com/demo/image/upload/sample_bp.jpg", # image_url
            "MED-BPM-002", # sku_id
            5, # quantity
            "set", # unit
            320.00, # regular_price
            280.00, # sale_price
            "available", # shipping_status
            False, # free_shipping
            15.00, # additional_shipping_charge
            "1-2 business days", # delivery_time
            5.00, # tax_percentage
            0.8, # weight
            20.0, # length
            20.0, # width
            15.0, # height
            "Automatic digital BP monitor with large display.", # features
            "<p>One-touch operation; Irregular heartbeat detection; Memory for 2 users.</p>", # overview
            "<p>Accuracy: +/- 3mmHg.</p>", # technical_info
            "<p>Standard shipping policy applies.</p>", # shipping_returns
            4.5, # avg_rating
            45, # review_count
            "TRENDING", # badge
            "red", # badge_color
            False, # exclusive_products
            True, # on_sale_now
            True, # is_active
            "2024-01-01 11:00:00", # created_at
            "Digital BP Monitor Dubai", # meta_title
            "Reliable blood pressure monitoring at home.", # meta_description
            "bp monitor, blood pressure, health, uae", # meta_keywords
            "", # gallery_image_urls
            "" # category_image_url
        ]
        
        # Helper to ensure exact length matching
        dataset.append(sample_row_1[:len(headers)])
        dataset.append(sample_row_2[:len(headers)])
            
        return dataset

    def download_demo_excel(self, request):
        dataset = self._get_demo_dataset()
        from django.http import HttpResponse
        response = HttpResponse(dataset.export('xlsx'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="product_import_demo.xlsx"'
        return response

    def download_demo_csv(self, request):
        dataset = self._get_demo_dataset()
        from django.http import HttpResponse
        response = HttpResponse(dataset.export('csv'), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="product_import_demo.csv"'
        return response

    class Media:
        js = (
            'admin/js/dynamic_categories.js',
        )
        css = {
            'all': ('admin/css/import_preview_fix.css',)
        }

    def preview(self, obj):
        url = obj.get_image_url
        if url:
            return mark_safe(f'<img src="{url}" class="admin-list-img" />')
        return "-"

    def category_display(self, obj):
        if not obj.category: return "-"
        if obj.category.parent:
            return mark_safe(f'<span style="color:#666; font-size:0.85em;">{obj.category.parent.name}</span><br><b>{obj.category.name}</b>')
        return obj.category.name
    category_display.short_description = "Category"

    def parent_category_display(self, obj):
        return obj.category.parent if obj.category and obj.category.parent else (obj.category if obj.category else "-")
    parent_category_display.short_description = "Parent Category"

    def badge_management(self, obj):
        if not obj.pk: return "Save product first to manage badges."
        badges = obj.trust_badges.all()
        if not badges: return "No badges assigned. Use checkboxes below to add."
        
        html = '<div style="display:flex; flex-wrap:wrap; gap:10px;">'
        for b in badges:
            edit_url = reverse('admin:products_trustbadge_change', args=[b.id])
            html += f'''
                <div style="background:{b.background_color}; color:{b.text_color}; border:1px solid {b.border_color}; 
                            padding:8px 12px; border-radius:12px; display:flex; align-items:center; gap:8px;">
                    <a href="{edit_url}" class="related-widget-wrapper-link change-related" style="color:inherit; text-decoration:none; font-size:10px; font-weight:900; text-transform:uppercase;">{b.name}</a>
                    <a href="{edit_url}" class="related-widget-wrapper-link change-related" title="Edit Badge">
                        <img src="/static/admin/img/icon-changelink.svg" alt="Edit" style="width:14px; height:14px; opacity:0.6 hover:opacity:1;">
                    </a>
                </div>
            '''
        html += '</div>'
        # Add a link to create new
        add_url = reverse('admin:products_trustbadge_add')
        html += f'<div style="margin-top:15px;"><a href="{add_url}" class="add-related" style="color:var(--primary); font-weight:bold; font-size:11px;">+ Add New Global Trust Badge</a></div>'
        return mark_safe(html)
    badge_management.short_description = "Manage Selected Badges"

    def stock_status(self, obj):
        return "✅ In Stock" if obj.is_in_stock() else "❌ Out of Stock"
    stock_status.short_description = "Stock"

    fieldsets = (
        ('Overview', {
            'fields': (
                'name', 
                'sku_id', 
                'parent_category', 
                'category',
                'brand', 
                'quantity',
                'avg_rating', 
                'review_count',
                'badge', 
                'badge_color',
                'slug', 
                'exclusive_products', 
                'on_sale_now'
            ),
            'description': 'Core identity and stock availability. Choose a parent category to see subcategories.'
        }),
        ('Pricing & Shipping', {
            'fields': ('regular_price', 'sale_price', 'shipping_status', 'delivery_time', 'tax_percentage', 'free_shipping', 'additional_shipping_charge'),
            'classes': ('collapse',),
        }),
        ('Dimensions & Weight', {
            'fields': ('weight', 'unit', 'length', 'width', 'height'),
            'classes': ('collapse',),
        }),
        ('Detailed Content', {
            'fields': ('overview', 'features', 'technical_info', 'shipping_returns'),
        }),
        ('Trust Signals & Badges', {
            'fields': ('badge_management', 'trust_badges'),
            'description': 'View/Edit assigned badges above or select new ones below.'
        }),
        ('Media Assets', {
            'fields': ('image', 'image_url'),
        }),
        ('Search Optimization', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )
    radio_fields = {
        "shipping_status": admin.HORIZONTAL,
        "free_shipping": admin.HORIZONTAL,
    }
    autocomplete_fields = ('brand',)

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('name', 'show_on_homepage', 'homepage_order', 'parent', 'is_active', 'category_image')
    list_editable = ('show_on_homepage', 'homepage_order')
    list_filter = ('show_on_homepage',)
    search_fields = ('name', 'slug')
    autocomplete_fields = ('parent',)
    inlines = [SubCategoryInline]
    prepopulated_fields = {"slug": ("name",)}

    def category_image(self, obj):
        url = obj.get_image_url
        if url:
            return mark_safe(f'<img src="{url}" class="admin-list-img" />')
        return "-"
    category_image.short_description = "Image"
    
    def get_queryset(self, request):
        """Only show root categories in the main list."""
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)
    
    fieldsets = (
        ('Hierarchy & Branding', {
            'fields': (
                'name', 
                'parent', 
                'slug', 
                'homepage_order', 
                'image', 
                'image_url',
                'icon_svg',
                'show_on_homepage',
                'description'
            )
        }),
        ('Search Optimization', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )
    radio_fields = {
        "show_on_homepage": admin.HORIZONTAL,
    }

    class Media:
        css = {
            'all': ('admin/css/subcategory_admin.css',)
        }

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'show_on_homepage', 'order', 'brand_logo')
    list_editable = ('show_on_homepage', 'order')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ('Brand Identity', {
            'fields': ('name', 'slug', 'order'),
        }),
        ('Visuals & Branding', {
            'fields': ('logo', 'logo_url', 'description'),
            'description': 'Upload a brand logo or provide an external URL.'
        }),
        ('Homepage Appearance', {
            'fields': ('show_on_homepage',),
            'description': 'Toggle visibility in the "We Deal With" section on the homepage.'
        }),
        ('SEO Presence', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )
    radio_fields = {"show_on_homepage": admin.HORIZONTAL}

    def brand_logo(self, obj):
        url = obj.get_image_url
        if url:
            return mark_safe(f'<img src="{url}" class="admin-list-img" />')
        return "-"
    brand_logo.short_description = 'Logo'

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('name', 'offer_type', 'discount_value', 'start_date', 'end_date')
    list_filter = ('offer_type',)
    search_fields = ('name',)
    filter_horizontal = ('products', 'categories', 'brands')

    fieldsets = (
        ('Offer Basics', {
            'fields': ('name', 'offer_type', 'discount_value')
        }),
        ('Active Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Bulk Assignment', {
            'fields': ('categories', 'brands'),
            'description': 'Select categories or brands to apply this offer to all their products automatically.'
        }),
        ('Individual Products', {
            'fields': ('products',),
            'description': 'Use the selector below to assign this offer to specific products manually.'
        }),
    )

    class Media:
        css = {'all': ('admin/css/admin_offer.css',)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.contrib import messages
        messages.success(request, f'🏷️ Offer "{obj.name}" has been saved.')

    def delete_model(self, request, obj):
        name = obj.name
        super().delete_model(request, obj)
        from django.contrib import messages
        messages.error(request, f'🗑️ Offer "{name}" was removed.')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_order', 'banner_preview')
    list_editable = ('display_order',)
    
    def banner_preview(self, obj):
        url = obj.get_image_url
        if url:
            return mark_safe(f'<img src="{url}" class="admin-list-img" />')
        return "-"
    banner_preview.short_description = 'Banner'
    filter_horizontal = ('products',)
    radio_fields = {}
    
    fieldsets = (
        ('Collection Info', {
            'fields': (('name', 'slug'), ('display_order')),
        }),
        ('Branding', {
            'fields': (('banner', 'banner_url'),),
        }),
        ('Products', {
            'fields': ('products',),
            'description': 'Select the products to include in this collection.'
        }),
    )

    class Media:
        css = {'all': ('admin/css/admin_offer.css',)}

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.contrib import messages
        messages.success(request, f'📦 Collection "{obj.name}" has been saved.')

    def delete_model(self, request, obj):
        name = obj.name
        super().delete_model(request, obj)
        from django.contrib import messages
        messages.error(request, f'🗑️ Collection "{name}" was removed.')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__username', 'product__name')

@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'color_preview')
    search_fields = ('name',)
    
    def color_preview(self, obj):
        return mark_safe(f'<div style="width:20px; height:20px; background:{obj.background_color}; border:1px solid {obj.border_color}; border-radius:4px;"></div>')
    color_preview.short_description = "Color"
