from django.db import models
from .design_models import DesignSettings

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default="Demo International")
    company_name = models.CharField(max_length=255, blank=True, help_text="Used in the header and copyright.")
    logo = models.ImageField(
        upload_to="settings/", 
        null=True, 
        blank=True,
        help_text="Primary Brand Logo. Recommended: 500x120px (Transparent PNG). Max 1MB."
    )
    logo_url = models.URLField(blank=True, null=True)
    favicon = models.ImageField(
        upload_to="settings/", 
        null=True, 
        blank=True,
        help_text="Browser Icon. Recommended: 32x32px or 64x64px. ICO or PNG."
    )
    favicon_url = models.URLField(blank=True, null=True)
    fav_text = models.CharField(max_length=50, default="Demo", help_text="Small text shown near favicon or in tab.")
    
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=512, blank=True, help_text="Global SEO Keywords.")
    
    # ── Tracking & SEO Analytics ───────────────────────────────────────────
    google_analytics_id = models.CharField(max_length=100, blank=True, help_text="GA4 Measurement ID (e.g. G-XXXXXXX)")
    facebook_pixel_id = models.CharField(max_length=100, blank=True, help_text="Meta Pixel ID")
    google_site_verification_id = models.CharField(max_length=255, blank=True, help_text="Verification token for Google Search Console.")
    robots_txt = models.TextField(blank=True, help_text="Custom robots.txt content. Leave blank to use default.")
    schema_markup = models.TextField(blank=True, help_text="Custom JSON-LD schema markup for the homepage.")

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    branch1_name = models.CharField(max_length=100, default="Dubai")
    dubai_address = models.TextField(blank=True, verbose_name="Branch 1 Address")
    branch2_name = models.CharField(max_length=100, default="Abu Dhabi")
    abudhabi_address = models.TextField(blank=True, verbose_name="Branch 2 Address")
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=100, default="@demo_intl", blank=True)
    
    
    
    
    
    

    
    # ── Footer Settings ───────────────────────────────────────────────────
    footer_quick_links_title = models.CharField(max_length=100, default="Quick Links")
    footer_support_title = models.CharField(max_length=100, default="Support")
    footer_legal_title = models.CharField(max_length=100, default="Legal")
    footer_newsletter_title = models.CharField(max_length=255, default="Subscribe to our Newsletter")
    footer_copyright_text = models.CharField(max_length=255, default="All rights reserved.", blank=True)
    
    # ── Notification Settings ───────────────────────────────────────────────
    enable_email_notifications    = models.BooleanField(default=True, verbose_name="Email Notifications", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_sms_notifications      = models.BooleanField(default=False, verbose_name="SMS Notifications", choices=((True, 'Enabled'), (False, 'Disabled')))
    enable_whatsapp_notifications = models.BooleanField(default=False, verbose_name="WhatsApp Notifications", choices=((True, 'Enabled'), (False, 'Disabled')))



    @property
    def get_image_url(self):
        if self.logo:
            try:
                return self.logo.url
            except (ValueError, AttributeError):
                pass
        if self.logo_url:
            return self.logo_url
        return "/static/assets/logo.png"

    def __str__(self): return "Global Site Settings"
    class Meta:
        verbose_name = "Website Settings"
        verbose_name_plural = "Website Settings"

class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    image = models.ImageField(
        upload_to="testimonials/", 
        null=True, 
        blank=True,
        help_text="Client Photo. Recommended: 200x200px (1:1). JPG, PNG. Max 500KB."
    )
    image_url = models.URLField(blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, help_text="Alt text for the client photo.")
    rating = models.PositiveIntegerField(default=5)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))
    class Meta: ordering = ['order']
    def __str__(self): return f"Testimonial from {self.client_name}"
    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/100"

class Client(models.Model):
    CATEGORY_CHOICES = (('Public', 'Public Sector'), ('Private', 'Private Sector'))
    name = models.CharField(max_length=100)
    logo = models.ImageField(
        upload_to="clients/", 
        null=True, 
        blank=True,
        help_text="Client Logo. Recommended: 300x120px (Transparent PNG). Max 500KB."
    )
    logo_url = models.URLField(blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, help_text="Alt text for the client logo.")
    icon_svg = models.TextField(blank=True, help_text="Paste SVG code for logo here.")
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Public')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))
    class Meta: ordering = ['order']
    def __str__(self): return self.name
    @property
    def get_image_url(self):
        if self.logo:
            try:
                return self.logo.url
            except (ValueError, AttributeError):
                pass
        if self.logo_url:
            return self.logo_url
        return "https://via.placeholder.com/150x60"

class SocialPost(models.Model):
    image = models.ImageField(
        upload_to="social/", 
        null=True, 
        blank=True,
        help_text="Instagram Preview. Recommended: 1080x1080px (Square). JPG, WEBP. Max 2MB."
    )
    image_url = models.URLField(blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, help_text="Alt text for the social post image.")
    icon_svg = models.TextField(blank=True, help_text="Paste SVG code here.")
    link = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/400"

class StoreLocation(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to="stores/", 
        null=True, 
        blank=True,
        help_text="Storefront Photo. Recommended: 800x600px. JPG, WEBP. Max 1MB."
    )
    image_url = models.URLField(blank=True, null=True, help_text="Alternative: Direct link to an externally hosted image.")
    image_alt = models.CharField(max_length=255, blank=True, help_text="Alt text for the store photo.")
    address = models.TextField()
    city = models.CharField(max_length=100, help_text="e.g. Dubai, Sharjah, Abu Dhabi")
    phone = models.CharField(max_length=50)
    map_url = models.URLField(verbose_name="Google Maps URL", help_text="Link to the location on Google Maps (Get Directions)")
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))
    order = models.PositiveIntegerField(default=0, verbose_name="Sort Order")

    class Meta:
        ordering = ['order', 'name']

    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/600x400"

    def __str__(self):
        return f"{self.name} ({self.city})"

class AnnouncementBar(models.Model):
    text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))
    background_color = models.CharField(max_length=50, default="#000000")
    text_color = models.CharField(max_length=50, default="#ffffff")
    closable = models.BooleanField(default=True, verbose_name="User Closable", choices=((True, 'Yes'), (False, 'No')))
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self): return self.text
    class Meta:
        verbose_name = "Top Bar Message"
        verbose_name_plural = "Top Bar Messages"

class SearchIndex(models.Model):
    product_name = models.CharField(max_length=255)
    keywords = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(blank=True)

    def __str__(self): return self.product_name


class NewsletterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self): return self.email

    class Meta:
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        ordering = ['-subscribed_at']
