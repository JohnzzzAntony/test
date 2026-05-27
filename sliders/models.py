from django.db import models

class HeroSlider(models.Model):
    badge_text = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    image = models.ImageField(
        upload_to="sliders/", 
        null=True, 
        blank=True,
        help_text="Desktop slider image. Recommended: 1920x800px. JPG, WEBP. Max 2MB."
    )
    image_url = models.URLField(blank=True, null=True, help_text="External URL for background image.")
    image_alt = models.CharField(max_length=255, blank=True, help_text="Alt text for the slider background image.")
    video = models.FileField(
        upload_to="sliders/videos/", 
        null=True, 
        blank=True,
        help_text="Background video. Recommended: MP4 format. Max 5MB for performance."
    )
    video_url = models.URLField(blank=True, null=True, help_text="External URL for background video (YouTube/Vimeo not supported for direct background).")
    
    # ── 3D Visuals ────────────────────────────────────────────────────────
    threejs_model_path = models.CharField(max_length=500, blank=True, null=True, help_text="Path to GLTF/GLB model in static files.")
    enable_3d_overlay = models.BooleanField(default=False, help_text="Overlay an interactive 3D scene on this banner.")
    threejs_intensity = models.FloatField(default=1.0, help_text="Opacity/Brightness of the 3D effect.")
    
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))

    @property
    def get_image_url(self):
        try:
            if self.image: return self.image.url
            if self.image_url: return self.image_url
        except Exception: pass
        return "https://via.placeholder.com/1920x800"

    def get_vid_url(self):
        if self.video_url: return self.video_url
        return self.video.url if self.video else ""

    def __str__(self): return self.title if self.title else f"Banner {self.pk or 'New'}"
    class Meta:
        ordering = ['order']
        verbose_name = "Banner"
        verbose_name_plural = "Banners"

class PromoBanner(models.Model):
    LAYOUT_CHOICES = [
        ('1_col', '1-Column (Full Width)'),
        ('2_col', '2-Column (Side by Side)'),
        ('3_col', '3-Column (Row)'),
        ('mosaic', 'Mosaic/Grid'),
    ]
    SHAPE_CHOICES = [
        ('rectangular', 'Rectangular'),
        ('rounded', 'Rounded Corners'),
        ('pill', 'Pill Shape'),
    ]
    
    name = models.CharField(max_length=100, help_text="Internal name for management.")
    layout = models.CharField(max_length=20, choices=LAYOUT_CHOICES, default='1_col')
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, default='rounded')
    homepage_order = models.PositiveIntegerField(default=0, help_text="Order in which this banner appears on homepage.")
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Removed')))
    
    def __str__(self): return f"{self.name} ({self.get_layout_display()})"
    class Meta:
        ordering = ['homepage_order']
        verbose_name = "Promo Section"
        verbose_name_plural = "Promo Sections"

class BannerItem(models.Model):
    banner_section = models.ForeignKey(PromoBanner, related_name='items', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banners/', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True, help_text="Direct link if image is externally hosted.")
    image_alt = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, help_text="Link path (e.g., /shop/ or full URL).")
    title = models.CharField(max_length=255, blank=True, help_text="Optional overlay text.")
    subtitle = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    @property
    def get_image_url(self):
        try:
            if self.image:
                url = self.image.url
                if url.startswith('/media/media/'):
                    return url.replace('/media/media/', '/media/', 1)
                return url
            if self.image_url: return self.image_url
        except Exception: pass
        return "https://via.placeholder.com/600x400"

    def __str__(self): return f"Item {self.order} for {self.banner_section.name}"
    class Meta:
        ordering = ['order']
