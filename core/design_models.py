from django.db import models

class DesignSettings(models.Model):
    # ── Flower District Theme - Deep Blue Professional Palette ─────────────────
    primary_color = models.CharField(max_length=50, default="#114084", help_text="Primary Brand Color (Deep Blue).")
    secondary_color = models.CharField(max_length=50, default="#1a5cb8", help_text="Secondary Blue for hover states.")
    accent_color = models.CharField(max_length=50, default="#0081ff", help_text="Bright Blue accent for CTAs and highlights.")
    accent_hover_color = models.CharField(max_length=50, default="#0066cc", help_text="Accent color for hover states.")

    text_primary_color = models.CharField(max_length=50, default="#1a1a1a", help_text="Main text color (Near Black).")
    text_secondary_color = models.CharField(max_length=50, default="#666666", help_text="Muted text/labels.")
    text_white_color = models.CharField(max_length=50, default="#FFFFFF", help_text="Pure white text.")
    text_accent_color = models.CharField(max_length=50, default="#114084", help_text="Accent text color.")

    surface_bg_color = models.CharField(max_length=50, default="#FFFFFF", help_text="Main site background (Clean White).")
    card_bg_color = models.CharField(max_length=50, default="#FFFFFF", help_text="Card/Container background.")
    border_color = models.CharField(max_length=50, default="#e5e5e5", help_text="Dividers, card borders.")
    border_hover_color = models.CharField(max_length=50, default="#cccccc", help_text="Border color on hover.")

    header_bg_color = models.CharField(max_length=50, default="#FFFFFF")
    header_text_color = models.CharField(max_length=50, default="#1a1a1a")
    header_border_color = models.CharField(max_length=50, default="#e5e5e5")
    footer_bg_color = models.CharField(max_length=50, default="#1a1a1a")
    footer_text_color = models.CharField(max_length=50, default="#f5f5f5")
    footer_heading_color = models.CharField(max_length=50, default="#FFFFFF")

    # ── Category & Product Specific Colors ─────────────────────────────────────
    category_bg_color = models.CharField(max_length=50, default="#f8f9fa", help_text="Category section background.")
    price_color = models.CharField(max_length=50, default="#1a1a1a", help_text="Product price text color.")
    sale_price_color = models.CharField(max_length=50, default="#c0392b", help_text="Sale price color.")
    rating_star_color = models.CharField(max_length=50, default="#f59e0b", help_text="Rating star color.")

    # ── Button Colors ───────────────────────────────────────────────────────────
    button_primary_bg = models.CharField(max_length=50, default="#114084", help_text="Primary button background.")
    button_primary_text = models.CharField(max_length=50, default="#FFFFFF", help_text="Primary button text.")
    button_primary_hover_bg = models.CharField(max_length=50, default="#0d3a6e", help_text="Primary button hover background.")
    button_secondary_bg = models.CharField(max_length=50, default="#FFFFFF", help_text="Secondary button background.")
    button_secondary_text = models.CharField(max_length=50, default="#114084", help_text="Secondary button text.")
    button_secondary_border = models.CharField(max_length=50, default="#114084", help_text="Secondary button border.")
    button_secondary_hover_bg = models.CharField(max_length=50, default="#114084", help_text="Secondary button hover background.")
    button_secondary_hover_text = models.CharField(max_length=50, default="#FFFFFF", help_text="Secondary button hover text.")

    # ── Typography Hierarchy ─────────────────────────────────────────
    FONT_CHOICES = (
        ("'Inter', sans-serif", "Inter (Clean UI - Primary)"),
        ("'Montserrat', sans-serif", "Montserrat (Versatile UI)"),
        ("'Poppins', sans-serif", "Poppins (Modern Geometric)"),
        ("'Roboto', sans-serif", "Roboto (Material Design)"),
        ("'Open Sans', sans-serif", "Open Sans (Highly Readable)"),
        ("'Oswald', sans-serif", "Oswald (Condensed Display)"),
        ("'Playfair Display', serif", "Playfair Display (Premium Serif)"),
        ("'Cormorant Garamond', serif", "Cormorant Garamond (Elegant Serif)"),
    )
    font_main = models.CharField(max_length=100, choices=FONT_CHOICES, default="'Inter', sans-serif", help_text="Primary font for body text, buttons, navigation")
    font_heading = models.CharField(max_length=100, choices=FONT_CHOICES, default="'Montserrat', sans-serif", help_text="Display font for headings and major titles")
    font_accent = models.CharField(max_length=100, choices=FONT_CHOICES, default="'Playfair Display', serif", help_text="Premium serif for logo, brand name, and accent sections")

# ── Shapes & Radius ─────────────────────────────────────────
    container_radius = models.CharField(max_length=50, default="8px", help_text="e.g. 8px, 0.5rem for main containers")
    card_radius = models.CharField(max_length=50, default="8px", help_text="e.g. 8px for cards")
    button_radius = models.CharField(max_length=50, default="4px", help_text="e.g. 4px (Subtle), 9999px (Pill)")
    image_radius = models.CharField(max_length=50, default="8px")
    input_radius = models.CharField(max_length=50, default="4px", help_text="Form input border radius")

    # ── Global UI Scaling ─────────────────────────────────────────
    site_scale = models.DecimalField(max_digits=3, decimal_places=2, default=1.0, help_text="Global site scale factor (e.g. 0.9 = 90% size at 100% browser zoom)")

    # ── Visual Effects ────────────────────────────────────────────
    enable_shadows = models.BooleanField(default=True, verbose_name="Card Shadows", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_hover_effects = models.BooleanField(default=True, verbose_name="Hover Effects", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_animations = models.BooleanField(default=True, verbose_name="Scroll Animations", choices=((True, 'Enabled'), (False, 'Disabled')))

    ANIMATION_EFFECTS = (
        ('fade-up', 'Fade Up'),
        ('fade-down', 'Fade Down'),
        ('zoom-in', 'Zoom In'),
        ('slide-left', 'Slide Left'),
        ('none', 'No Animation'),
    )
    global_animation_type = models.CharField(max_length=20, choices=ANIMATION_EFFECTS, default='fade-up')
    animation_duration = models.PositiveIntegerField(default=400, help_text="Animation duration in ms")

    # ── Spacing Scale ─────────────────────────────────────────────
    spacing_unit = models.PositiveIntegerField(default=8, help_text="Base spacing unit in px (e.g. 8 for 8px scale)")
    section_padding = models.PositiveIntegerField(default=64, help_text="Section padding in px")
    container_padding = models.PositiveIntegerField(default=48, help_text="Container padding in px")

    # ── Homepage Section Titles ─────────────────────────────────────────────
    hp_hero_title = models.CharField(max_length=255, default='Premium <span class="accent">Flowers</span> & Gifts')
    hp_hero_subtitle = models.TextField(default='Discover elegant floral arrangements for every occasion.', blank=True)

    hp_collections_title = models.CharField(max_length=255, default='Exclusive <span class="accent">Collections</span>')
    hp_collections_subtitle = models.TextField(default='Handpicked selection of premium floral arrangements.', blank=True)

    hp_categories_title = models.CharField(max_length=255, default='Shop by <span class="accent">Category</span>')

    hp_latest_products_title = models.CharField(max_length=255, default='Latest <span class="accent">Products</span>')
    hp_latest_products_subtitle = models.TextField(default='Discover our newest floral creations.', blank=True)

    hp_bestsellers_title = models.CharField(max_length=255, default='Our Best <span class="accent">Sellers</span>')

    hp_partners_title = models.CharField(max_length=255, default="Our Partners")
    hp_services_title = models.CharField(max_length=255, default="Why Choose Us")
    hp_gallery_title = models.CharField(max_length=255, default='Our <span class="accent">Gallery</span>')
    hp_testimonials_title = models.CharField(max_length=255, default="What Our Customers Say")
    hp_clients_title = models.CharField(max_length=255, default="Trusted By")
    hp_social_title = models.CharField(max_length=255, default="Follow Us")

    # ── App-Wide Section Titles ─────────────────────────────────────────────
    cart_page_title = models.CharField(max_length=255, default='Your <span class="accent">Cart</span>')
    wishlist_page_title = models.CharField(max_length=255, default='My <span class="accent">Wishlist</span>')
    search_page_title = models.CharField(max_length=255, default='Search <span class="accent">Results</span>')
    checkout_page_title = models.CharField(max_length=255, default='Secure <span class="accent">Checkout</span>')
    profile_page_title = models.CharField(max_length=255, default='My <span class="accent">Account</span>')
    orders_page_title = models.CharField(max_length=255, default='Order <span class="accent">History</span>')
    contact_page_title = models.CharField(max_length=255, default='Contact <span class="accent">Us</span>')

    # ── Component Visibility (Header) ─────────────────────────────
    show_header_search = models.BooleanField(default=True, verbose_name="Header Search", choices=((True, 'Show'), (False, 'Hide')))
    show_header_wishlist = models.BooleanField(default=True, verbose_name="Header Wishlist", choices=((True, 'Show'), (False, 'Hide')))
    show_header_account = models.BooleanField(default=True, verbose_name="Header Account", choices=((True, 'Show'), (False, 'Hide')))
    show_header_cart = models.BooleanField(default=True, verbose_name="Header Cart", choices=((True, 'Show'), (False, 'Hide')))

    # ── Homepage Section Visibility ──────────────────────────────
    show_hp_categories = models.BooleanField(default=True, verbose_name="Home Categories", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_collections = models.BooleanField(default=True, verbose_name="Home Collections", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_latest_products = models.BooleanField(default=True, verbose_name="Home Latest Products", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_bestsellers = models.BooleanField(default=True, verbose_name="Home Best Sellers", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_brands = models.BooleanField(default=True, verbose_name="Home Brands", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_testimonials = models.BooleanField(default=True, verbose_name="Home Testimonials", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_clients = models.BooleanField(default=True, verbose_name="Home Clients", choices=((True, 'Show'), (False, 'Hide')))
    show_hp_social = models.BooleanField(default=True, verbose_name="Home Social", choices=((True, 'Show'), (False, 'Hide')))

    # ── Product Display Settings ────────────────────────────────────────────
    pd_related_title = models.CharField(max_length=255, default="You May Also Like")
    pd_show_related = models.BooleanField(default=True, verbose_name="Related Products", choices=((True, 'Show'), (False, 'Hide')))
    pd_related_count = models.PositiveIntegerField(default=4)

    # ── Counter Animations ──────────────────────────────────────────────────
    counter_animation_style = models.CharField(max_length=50, default='fade')
    counter_animation_speed = models.PositiveIntegerField(default=2000)

    # ── Trust Badge Icons (Homepage) ────────────────────────────────────────
    show_trust_badges = models.BooleanField(default=True, verbose_name="Trust Badges", choices=((True, 'Show'), (False, 'Hide')))
    trust_badge_1_title = models.CharField(max_length=100, default="Fast Delivery")
    trust_badge_1_text = models.CharField(max_length=200, default="Safe & fast deliveries all over UAE")
    trust_badge_2_title = models.CharField(max_length=100, default="Secure Payment")
    trust_badge_2_text = models.CharField(max_length=200, default="VISA, Mastercard and Cash on Delivery")
    trust_badge_3_title = models.CharField(max_length=100, default="Customer Support")
    trust_badge_3_text = models.CharField(max_length=200, default="We are here 24/7 for your queries")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Theme Settings"
        verbose_name_plural = "Theme Settings"

    def __str__(self):
        return "Global Design Configuration"
