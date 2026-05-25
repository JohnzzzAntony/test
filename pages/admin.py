from django.contrib import admin
from .models import (
    PageHero, AboutUs, VideoCard, MissionVision, Service, Counter,
    WhyUsCard, GalleryItem, Partner, ContactPage,
    HeroSlide, HomepageSettings,
)
from django.utils.html import format_html

@admin.register(PageHero)
class PageHeroAdmin(admin.ModelAdmin):
    list_display = ('page', 'title', 'is_active', 'hero_preview')
    list_editable = ('is_active',)
    readonly_fields = ('frontend_preview', 'hero_preview')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Live Preview', {
            'fields': ('frontend_preview',),
            'description': 'This shows how the hero currently looks on the frontend (including defaults if fields are left blank).'
        }),
        ('Reference', {
            'fields': ('page', 'is_active'),
        }),
        ('Hero Identity', {
            'fields': ('title', 'title_html', 'subtitle', 'alignment'),
        }),
        ('Call to Action', {
            'fields': (('button_text', 'button_link'), ('button_2_text', 'button_2_link')),
        }),
        ('Imagery', {
            'fields': ('hero_preview', ('hero_image', 'hero_image_url'),),
        }),
        ('SEO Optimization', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
        }),
    )
    
    def frontend_preview(self, obj):
        from django.utils.safestring import mark_safe
        if not obj.page:
            return "Save to see preview"
            
        # Get current display values (server-side logic)
        title = obj.display_title
        subtitle = obj.display_subtitle
        image = obj.display_image
        
        # Base defaults for JS fallbacks
        defaults = {
            'about': {
                'title': 'Our Legacy',
                'subtitle': 'Defining excellence in the international trade landscape for over a decade.',
                'image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069'
            },
            'products': {
                'title': 'Our Products',
                'subtitle': 'Explore our wide range of premium products.',
                'image': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-2.jpg'
            },
            'services': {
                'title': 'Our Solutions',
                'subtitle': 'Discover our range of professional healthcare services, from equipment installation to staff training and preventive maintenance.',
                'image': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80'
            },
            'gallery': {
                'title': 'Our Gallery',
                'subtitle': 'A glimpse into our work and achievements.',
                'image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069'
            },
            'brands': {
                'title': 'Trusted Brands',
                'subtitle': 'Our curated network of world-class medical equipment manufacturers.',
                'image': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-2.jpg'
            },
            'stores': {
                'title': 'Our Stores',
                'subtitle': 'Find a JKR store near you.',
                'image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069'
            },
            'blog': {
                'title': 'Latest News',
                'subtitle': 'Stay updated with our latest stories and articles.',
                'image': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069'
            },
            'contact': {
                'title': 'Contact Us',
                'subtitle': 'Have questions? We would love to hear from you.',
                'image': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070'
            }
        }
        
        default = defaults.get(obj.page, {})
        
        # Try to get dynamic defaults from settings models for JS fallback
        if obj.page == 'about':
            try:
                about = AboutUs.objects.first()
                if about:
                    default['title'] = about.legacy_title or default['title']
                    default['subtitle'] = about.legacy_subtitle or default['subtitle']
            except: pass
        elif obj.page == 'contact':
            try:
                contact = ContactPage.objects.first()
                if contact:
                    default['title'] = contact.heading_html or default['title']
                    default['subtitle'] = contact.subtitle or default['subtitle']
            except: pass

        # Determine alignment flex value
        if obj.alignment == 'left':
            align = 'flex-start'
            text_align = 'left'
        elif obj.alignment == 'right':
            align = 'flex-end'
            text_align = 'right'
        else:
            align = 'center'
            text_align = 'center'
            
        import json
        js_defaults = json.dumps(default)

        return format_html(
            '<div style="position: relative; width: 100%; max-width: 800px; height: 250px; border-radius: 12px; overflow: hidden; background: #010101; font-family: sans-serif; border: 1px solid #eee;">'
            '<img id="preview-img" src="{}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0.6;" />'
            '<div style="position: absolute; inset: 0; background: linear-gradient(rgba(0,0,0,0.4), transparent);"></div>'
            '<div id="preview-content" style="position: relative; z-index: 10; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: {}; text-align: {}; padding: 40px; color: white;">'
            '<h1 id="preview-title" style="font-size: 34px; font-weight: 900; margin: 0 0 12px 0; text-shadow: 2px 2px 8px rgba(0,0,0,0.8); line-height: 1.1; letter-spacing: -0.02em;">{}</h1>'
            '<p id="preview-subtitle" style="font-size: 16px; margin: 0; max-width: 85%; text-shadow: 1px 1px 4px rgba(0,0,0,0.8); opacity: 0.9; font-weight: 500;">{}</p>'
            '</div>'
            '<script>'
            '(function() {{'
            '    const defaults = {};'
            '    const titleInput = document.getElementById("id_title");'
            '    const titleHtmlInput = document.getElementById("id_title_html");'
            '    const subtitleInput = document.getElementById("id_subtitle");'
            '    const alignInput = document.getElementById("id_alignment");'
            '    const urlInput = document.getElementById("id_hero_image_url");'
            '    const fileInput = document.getElementById("id_hero_image");'
            '    '
            '    const previewTitle = document.getElementById("preview-title");'
            '    const previewSubtitle = document.getElementById("preview-subtitle");'
            '    const previewImg = document.getElementById("preview-img");'
            '    const previewContent = document.getElementById("preview-content");'
            '    '
            '    function update() {{'
            '        if (titleHtmlInput && titleHtmlInput.value) {{'
            '            previewTitle.innerHTML = titleHtmlInput.value;'
            '        }} else if (titleInput && titleInput.value) {{'
            '            previewTitle.innerText = titleInput.value;'
            '        }} else {{'
            '            previewTitle.innerText = defaults.title || "Hero Title";'
            '        }}'
            '        '
            '        if (subtitleInput && subtitleInput.value) {{'
            '            previewSubtitle.innerText = subtitleInput.value;'
            '        }} else {{'
            '            previewSubtitle.innerText = defaults.subtitle || "Hero Subtitle";'
            '        }}'
            '        '
            '        if (urlInput && urlInput.value) {{'
            '            previewImg.src = urlInput.value;'
            '        }} else if (!fileInput || !fileInput.files || !fileInput.files[0]) {{'
            '            previewImg.src = defaults.image || "";'
            '        }}'
            '        '
            '        if (alignInput) {{'
            '            const align = alignInput.value;'
            '            if (align === "left") {{'
            '                previewContent.style.alignItems = "flex-start";'
            '                previewContent.style.textAlign = "left";'
            '            }} else if (align === "right") {{'
            '                previewContent.style.alignItems = "flex-end";'
            '                previewContent.style.textAlign = "right";'
            '            }} else {{'
            '                previewContent.style.alignItems = "center";'
            '                previewContent.style.textAlign = "center";'
            '            }}'
            '        }}'
            '    }}'
            '    '
            '    if (fileInput) {{'
            '        fileInput.addEventListener("change", function() {{'
            '            if (this.files && this.files[0]) {{'
            '                const reader = new FileReader();'
            '                reader.onload = function(e) {{'
            '                    previewImg.src = e.target.result;'
            '                }};'
            '                reader.readAsDataURL(this.files[0]);'
            '            }}'
            '        }});'
            '    }}'
            '    '
            '    [titleInput, titleHtmlInput, subtitleInput, alignInput, urlInput].forEach(el => {{'
            '        if (el) el.addEventListener("input", update);'
            '        if (el) el.addEventListener("change", update);'
            '    }});'
            '    '
            '    update();'
            '}})();'
            '</script>'
            '</div>',
            image,
            align,
            text_align,
            mark_safe(title),
            subtitle,
            mark_safe(js_defaults)
        )
    frontend_preview.short_description = "Live Frontend Preview"

    def hero_preview(self, obj):
        url = obj.get_image_url
        if not url:
            # Get fallback for list view
            defaults = {
                'about': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069',
                'products': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-2.jpg',
                'services': 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&q=80',
                'gallery': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069',
                'brands': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-2.jpg',
                'stores': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-1.jpg',
                'blog': 'https://jkrintl.com/wp-content/uploads/2022/12/JKR-Banner-2.jpg',
                'contact': 'https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069'
            }
            url = defaults.get(obj.page, "")
        
        return format_html('<img src="{}" style="height:50px; width: 120px; object-fit: cover; border-radius: 5px; border: 1px solid #eee;" />', url) if url else "-"
    hero_preview.short_description = 'Frontend Preview'

class VideoCardInline(admin.TabularInline):
    model = VideoCard
    extra = 0
    fields = ('title', 'video_url', ('thumbnail', 'thumbnail_url'), 'order')

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    inlines = [VideoCardInline]
    
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Brand Story', {
            'fields': (('title', 'heading'), 'is_active', 'content'),
        }),
        ('Cinematic Branding', {
            'fields': ('legacy_title', 'legacy_subtitle'),
        }),
        ('Experience Stats', {
            'fields': (('experience_value', 'experience_label'),),
        }),
    )

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

@admin.register(MissionVision)
class MissionVisionAdmin(admin.ModelAdmin):
    list_display = ('section_type', 'title')
    
    fieldsets = (
        ('Strategic Goal', {
            'fields': (('section_type', 'title'),),
        }),
        ('Content & Visuals', {
            'fields': ('content', ('image', 'image_url'), 'icon_svg'),
        }),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'image_tag')
    list_editable = ('order', 'is_active')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Service Info', {
            'fields': (('title', 'order'), 'is_active'),
        }),
        ('Appearance', {
            'fields': (('icon', 'icon_url'), 'icon_svg'),
        }),
        ('Narrative', {
            'fields': ('description',),
        }),
        ('SEO Optimization', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
        }),
    )
    
    def image_tag(self, obj):
        from django.utils.safestring import mark_safe
        if obj.icon_svg:
            return format_html('<div style="width: 45px; height: 45px; color: #007bff;">{}</div>', mark_safe(obj.icon_svg))
        url = obj.get_image_url
        return format_html('<img src="{}" style="width: 45px; height:45px; border-radius: 5px; object-fit: contain;" />', url) if url else "-"
    image_tag.short_description = 'Icon'

@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'order', 'is_active')
    list_editable = ('value', 'order', 'is_active')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Statistic', {
            'fields': (('title', 'value'), 'is_active'),
        }),
        ('Configuration', {
            'fields': ('icon_svg', 'order', 'svg_selection_helper'),
            'description': 'Paste an SVG code into the field above. You can use the quick-copy list below for common icons.'
        }),
    )
    readonly_fields = ('svg_selection_helper',)

    def svg_selection_helper(self, obj):
        icons = [
            ('Happy Clients', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'),
            ('Experience', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>'),
            ('Products', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>'),
            ('Global', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>'),
            ('Awards', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/></svg>'),
            ('Delivery', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17h4V5H2v12h3"/><path d="M20 17h2v-3.34a4 4 0 0 0-1.17-2.83L17 7h-3"/><circle cx="7.5" cy="17.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>'),
            ('Trusted', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'),
            ('Health', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'),
            ('Care', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/></svg>'),
            ('Location', '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>'),
        ]
        
        # Stylesheet for the helper
        styles = """
            <style>
                .svg-helper-container { background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; font-family: inherit; }
                .svg-helper-title { margin: 0 0 15px 0; font-weight: bold; color: #475569; display: flex; align-items: center; gap: 8px; }
                .svg-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(105px, 1fr)); gap: 12px; }
                .svg-card { background: #fff; text-align: center; cursor: pointer; padding: 12px; border: 1px solid #e2e8f0; border-radius: 10px; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
                .svg-card:hover { border-color: #2563eb; background: #f1f5f9; transform: translateY(-2px); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
                .svg-card-icon { color: #2563eb; margin-bottom: 8px; display: flex; justify-content: center; }
                .svg-card-name { font-size: 11px; color: #64748b; font-weight: 600; line-height: 1.2; display: block; }
                .svg-footer { margin-top: 20px; padding-top: 15px; border-top: 1px solid #e2e8f0; font-size: 13px; color: #64748b; }
                .svg-footer a { color: #2563eb; font-weight: bold; text-decoration: none; }
            </style>
        """

        html_parts = [styles, '<div class="svg-helper-container">']
        html_parts.append('<p class="svg-helper-title">✨ Quick Select Icons</p>')
        html_parts.append('<div class="svg-grid">')
        
        for name, code in icons:
            # Safely build each card
            card = format_html(
                '<div class="svg-card js-svg-selector" data-svg-code="{}">'
                '<div class="svg-card-icon">{}</div>'
                '<span class="svg-card-name">{}</span>'
                '</div>',
                code, 
                format_html('{}', code), 
                name
            )
            html_parts.append(card)
        
        html_parts.append('</div>')
        html_parts.append(
            '<div class="svg-footer">'
            'Need more? Visit <a href="https://lucide.dev/icons" target="_blank">Lucide Icons</a>, '
            'copy the "SVG" code, and paste it above.'
            '</div>'
            '<script>'
            'document.addEventListener("click", function(e) {'
            '    const card = e.target.closest(".js-svg-selector");'
            '    if (card) {'
            '        const svgCode = card.getAttribute("data-svg-code");'
            '        const input = document.getElementById("id_icon_svg");'
            '        if (input) {'
            '            input.value = svgCode;'
            '            card.style.borderColor = "#22c55e";'
            '            setTimeout(() => card.style.borderColor = "", 1000);'
            '        }'
            '    }'
            '});'
            '</script>'
        )
        html_parts.append('</div>')
        
        from django.utils.safestring import mark_safe
        return mark_safe(''.join(html_parts))
    svg_selection_helper.short_description = "Icon Selection Center"

@admin.register(WhyUsCard)
class WhyUsCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Advantage Card', {
            'fields': (('title', 'order'), 'is_active', 'description', 'icon_svg'),
        }),
    )

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'is_active', 'image_tag')
    list_editable = ('order', 'category', 'is_active')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Metadata', {
            'fields': (('title', 'category', 'order'), 'is_active'),
        }),
        ('Asset', {
            'fields': (('image', 'image_url'),),
        }),
    )
    
    def image_tag(self, obj):
        url = obj.get_image_url
        return format_html('<img src="{}" style="width: 60px; height:45px; border-radius: 5px; object-fit: cover;" />', url) if url else "-"
    image_tag.short_description = 'Image'

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website_url', 'order', 'is_active', 'image_tag')
    list_editable = ('order', 'is_active')
    radio_fields = {"is_active": admin.HORIZONTAL}
    
    fieldsets = (
        ('Company Details', {
            'fields': (('name', 'order'), 'is_active', 'website_url'),
        }),
        ('Branding', {
            'fields': (('logo', 'logo_url'), 'icon_svg'),
        }),
    )

    def image_tag(self, obj):
        url = obj.get_image_url
        return format_html('<img src="{}" style="height:45px; object-fit:contain; max-width: 120px;" />', url) if url else "-"
    image_tag.short_description = 'Logo'

@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'badge')
    fieldsets = (
        ('Hero Section', {
            'fields': ('badge', 'heading_html', 'subtitle'),
        }),
        ('Business Hours', {
            'fields': (('hours_label', 'hours_value'),),
        }),
        ('Inquiry Section', {
            'fields': ('form_title_html', 'form_subtitle', ('support_image', 'support_image_url')),
        }),
    )

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)


# ── Hero Slides ─────────────────────────────────────────────────────────────

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order', 'is_active', 'slide_preview')
    list_editable = ('order', 'is_active')
    list_per_page = 20
    radio_fields = {'is_active': admin.HORIZONTAL}

    fieldsets = (
        ('Slide Content', {
            'fields': (('title', 'order'), 'is_active', 'alt_text'),
        }),
        ('Image', {
            'fields': (('image', 'image_url'),),
            'description': (
                'Upload a portrait-oriented image (900 × 1100 px recommended) or paste an '
                'external URL. The image fills the right half of the homepage hero.'
            ),
        }),
    )

    def slide_preview(self, obj):
        url = obj.get_image_url
        if url:
            return format_html(
                '<img src="{}" style="height:60px;width:50px;object-fit:cover;'
                'border-radius:6px;border:1px solid #eee;" />',
                url
            )
        return '—'
    slide_preview.short_description = 'Preview'


# ── Homepage Settings ────────────────────────────────────────────────────────

@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    """
    Singleton admin — only one record is allowed.
    The admin hides the Add button when a record already exists.
    """

    fieldsets = (
        ('📢 Announcement Bar', {
            'fields': ('show_announcement_bar', 'announcement_text'),
            'description': 'Controls the slim dark bar at the top of the page.',
        }),
        ('🌸 Hero — Text & CTAs', {
            'fields': (
                'hero_eyebrow',
                'hero_title_line1', 'hero_title_em', 'hero_title_line2',
                'hero_subtitle',
                ('hero_btn1_text', 'hero_btn1_link'),
                ('hero_btn2_text', 'hero_btn2_link'),
            ),
            'description': (
                'Controls the text on the LEFT side of the hero. '
                'Add images on the RIGHT via <b>Hero Slides</b> above.'
            ),
        }),
        ('🏷️ Hero — Floating Tag', {
            'fields': ('show_hero_tag', 'hero_tag_label', 'hero_tag_value'),
            'description': 'The small glass card overlaid on the hero image.',
        }),
        ('📋 Section Labels', {
            'fields': (
                ('featured_eyebrow', 'featured_title'),
                'featured_subtitle',
                ('bestsellers_eyebrow', 'bestsellers_title'),
                ('testimonials_eyebrow', 'testimonials_title'),
            ),
        }),
        ('👁️ Section Visibility', {
            'fields': (
                'show_category_pills',
                'show_featured_products',
                'show_why_strip',
                'show_best_sellers',
                'show_testimonials',
            ),
            'description': 'Toggle individual sections on or off without deleting content.',
        }),
    )

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_object(self, request, object_id, from_field=None):
        # Auto-create the singleton if it doesn't exist yet
        HomepageSettings.get_settings()
        return super().get_object(request, object_id, from_field)
