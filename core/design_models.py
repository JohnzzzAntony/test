from django.db import models

class DesignSettings(models.Model):
    # ── Colors & Branding ───────────────────────────────────────────
    primary_color = models.CharField(max_length=50, default="#114084", help_text="Primary Brand Color (Buttons, Links, Accents).")
    secondary_color = models.CharField(max_length=50, default="#005CB9", help_text="Secondary/Hover states.")
    accent_glow_color = models.CharField(max_length=50, default="#0081ff", help_text="Ambient glow effects.")
    
    text_primary_color = models.CharField(max_length=50, default="#1e293b", help_text="Main text color.")
    text_secondary_color = models.CharField(max_length=50, default="#64748b", help_text="Muted text/labels.")
    text_white_color = models.CharField(max_length=50, default="#ffffff", help_text="Text on dark backgrounds.")
    
    surface_bg_color = models.CharField(max_length=50, default="#f8fafc", help_text="Main site background.")
    card_bg_color = models.CharField(max_length=50, default="#ffffff", help_text="Card/Container background.")
    border_color = models.CharField(max_length=50, default="#e2e8f0", help_text="Default border color.")
    
    header_bg_color = models.CharField(max_length=50, default="#ffffff")
    header_text_color = models.CharField(max_length=50, default="#1e293b")
    footer_bg_color = models.CharField(max_length=50, default="#1a1a1a")
    footer_text_color = models.CharField(max_length=50, default="#94a3b8")
    
    # ── Typography ───────────────────────────────────────────
    FONT_CHOICES = (
        ("'Noto Serif', serif", "Noto Serif (Classic/Premium)"),
        ("'Inter', sans-serif", "Inter (Modern/Clean)"),
        ("'Plus Jakarta Sans', sans-serif", "Jakarta (High-tech)"),
        ("'Montserrat', sans-serif", "Montserrat (Bold/Social)"),
    )
    font_main = models.CharField(max_length=100, choices=FONT_CHOICES, default="'Noto Serif', serif")
    font_secondary = models.CharField(max_length=100, choices=FONT_CHOICES, default="'Noto Serif', serif")
    
    # ── Shapes & Radius ───────────────────────────────────────────
    container_radius = models.CharField(max_length=50, default="40px", help_text="e.g. 40px, 2rem")
    card_radius = models.CharField(max_length=50, default="24px", help_text="e.g. 24px, 1.5rem")
    button_radius = models.CharField(max_length=50, default="9999px", help_text="e.g. 9999px (Pill), 12px (Soft)")
    image_radius = models.CharField(max_length=50, default="20px")

    # ── Visual Effects ────────────────────────────────────────────
    enable_glassmorphism = models.BooleanField(default=True, verbose_name="Glassmorphism", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_neumorphism = models.BooleanField(default=False, verbose_name="Neumorphism", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_ambient_glow = models.BooleanField(default=True, verbose_name="Ambient Glow", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_animations = models.BooleanField(default=True, verbose_name="Scroll Animations", choices=((True, 'Enabled'), (False, 'Disabled')))
    
    ANIMATION_EFFECTS = (
        ('fade-up', 'Fade Up'),
        ('fade-down', 'Fade Down'),
        ('zoom-in', 'Zoom In'),
        ('flip-left', 'Flip Left'),
        ('none', 'No Animation'),
    )
    global_animation_type = models.CharField(max_length=20, choices=ANIMATION_EFFECTS, default='fade-up')
    
    # ── Homepage Section Titles ─────────────────────────────────────────────
    hp_hero_title = models.CharField(max_length=255, default='Royal Quality <span class="italic">Healthcare</span>')
    hp_hero_subtitle = models.TextField(default='Precision medical equipment delivered with royalty-class service.', blank=True)
    
    hp_collections_title = models.CharField(max_length=255, default='Exclusive <span class="text-primary">Collections</span>')
    hp_collections_subtitle = models.TextField(default='Handpicked selection of premium medical equipment.', blank=True)
    hp_collections_badge = models.CharField(max_length=100, default='Curated Theme', blank=True)
    
    hp_categories_title = models.CharField(max_length=255, default='Product <span class="text-primary">Categories</span>')
    hp_categories_subtitle = models.TextField(default='Browse our extensive range of high-performance products, curated to meet the most demanding standards.', blank=True)
    hp_categories_badge = models.CharField(max_length=100, default='Discover Excellence', blank=True)
    
    hp_latest_products_title = models.CharField(max_length=255, default='Explore <span class="text-primary">Latest Products</span>')
    hp_latest_products_subtitle = models.TextField(default='Discover our newest medical innovations.', blank=True)
    hp_latest_products_badge = models.CharField(max_length=100, default='The Premium Standard', blank=True)
    
    hp_partners_title = models.CharField(max_length=255, default="Our Global Partners")
    hp_services_title = models.CharField(max_length=255, default="Maintenance Support")
    hp_gallery_title = models.CharField(max_length=255, default='Visual <span class="text-primary">Updates</span>')
    hp_testimonials_title = models.CharField(max_length=255, default="Client Testimonials")
    hp_clients_title = models.CharField(max_length=255, default="Trusted By")
    hp_social_title = models.CharField(max_length=255, default="Join Our Network")

    # ── App-Wide Section Titles ─────────────────────────────────────────────
    cart_page_title = models.CharField(max_length=255, default='Your <span class="italic text-primary">Cart</span>')
    wishlist_page_title = models.CharField(max_length=255, default='My <span class="italic text-primary">Wishlist</span>')
    search_page_title = models.CharField(max_length=255, default='Search <span class="text-primary">Results</span>')
    checkout_page_title = models.CharField(max_length=255, default='Secure <span class="text-primary">Checkout</span>')
    profile_page_title = models.CharField(max_length=255, default='My <span class="text-primary">Account</span>')
    orders_page_title = models.CharField(max_length=255, default='Order <span class="text-primary">History</span>')
    contact_page_title = models.CharField(max_length=255, default='Contact <span class="text-primary">Us</span>')

    # ── Component Visibility (Header) ─────────────────────────────
    show_header_search = models.BooleanField(default=True, verbose_name="Header Search", choices=((True, 'Show'), (False, 'Hide')))
    show_header_wishlist = models.BooleanField(default=True, verbose_name="Header Wishlist", choices=((True, 'Show'), (False, 'Hide')))
    show_header_account = models.BooleanField(default=True, verbose_name="Header Account", choices=((True, 'Show'), (False, 'Hide')))
    show_header_cart = models.BooleanField(default=True, verbose_name="Header Cart", choices=((True, 'Show'), (False, 'Hide')))

    # ── Homepage Section Visibility ──────────────────────────────
    show_hp_categories = models.BooleanField(default=True, verbose_name="Home Categories", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_collections = models.BooleanField(default=True, verbose_name="Home Collections", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_latest_products = models.BooleanField(default=True, verbose_name="Home Latest Products", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_brands = models.BooleanField(default=True, verbose_name="Home Brands", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_testimonials = models.BooleanField(default=True, verbose_name="Home Testimonials", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_clients = models.BooleanField(default=True, verbose_name="Home Clients", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_social = models.BooleanField(default=True, verbose_name="Home Social", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_counters = models.BooleanField(default=True, verbose_name="Home Counters", choices=((True, 'Show'), (False, 'Hide')))
    hp_counters_title = models.CharField(max_length=255, default='Our <span class="text-primary">Impact</span> in Numbers')
    hp_counters_subtitle = models.TextField(default="Quantifying our commitment to excellence and global reach.", blank=True)

    # ── Product Display Settings ────────────────────────────────────────────
    pd_related_title = models.CharField(max_length=255, default="You May Also Like")
    pd_show_related = models.BooleanField(default=True, verbose_name="Related Products", choices=((True, 'Show'), (False, 'Hide')))
    pd_related_count = models.PositiveIntegerField(default=4)

    # ── Counter Animations ──────────────────────────────────────────────────
    counter_animation_style = models.CharField(max_length=50, default='runner')
    counter_animation_speed = models.PositiveIntegerField(default=2000)

    # ── Luxury & 3D Settings ────────────────────────────────────────────────
    THREEJS_EFFECTS = (
        ('none', 'None'),
        ('particles', 'Particle Field'),
        ('fluid', 'Fluid Geometry'),
        ('floating_products', 'Floating Product Icons'),
        ('glass_shard', 'Glass Shards'),
    )
    hero_3d_effect = models.CharField(max_length=50, choices=THREEJS_EFFECTS, default='fluid')
    
    LUXURY_THEMES = (
        ('standard', 'Standard Professional'),
        ('luxury_dark', 'Luxury Midnight (Glassmorphism)'),
        ('high_tech', 'High-Tech (Glow/Neon)'),
        ('minimal_art', 'Minimal Artistic'),
    )
    ui_theme_variant = models.CharField(max_length=50, choices=LUXURY_THEMES, default='luxury_dark')
    
    enable_custom_cursor = models.BooleanField(default=True, help_text="Sleek magnetic follower cursor.")
    enable_magnetic_hover = models.BooleanField(default=True, help_text="Buttons and icons pull the cursor towards them.")
    enable_page_transitions = models.BooleanField(default=True, help_text="Smooth fade/slide between pages.")

    class Meta:
        verbose_name = "Theme Settings"
        verbose_name_plural = "Theme Settings"

    def __str__(self):
        return "Global Design Configuration"
