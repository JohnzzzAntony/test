from django.db import models, transaction
from django.db.models import Q
from django.utils.text import slugify
from django.utils import timezone
from ckeditor.fields import RichTextField
from decimal import Decimal, InvalidOperation
import uuid
try:
    from cloudinary_storage.storage import RawMediaCloudinaryStorage
    _raw_storage = RawMediaCloudinaryStorage()
except ImportError:
    _raw_storage = None

# ─── Category ────────────────────────────────────────────────────────────────

class Category(models.Model):
    parent = models.ForeignKey(
        'self', 
        related_name='subcategories', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        db_index=True,
        help_text="The immediate parent of this category. Leave blank for a top-level category."
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True, help_text="Optional description for SEO and category page header.")
    image = models.ImageField(
        upload_to='categories/', 
        null=True, 
        blank=True, 
        help_text="Recommended: 512x512px. JPG, PNG, WEBP. Max 1MB."
    )
    image_url = models.URLField(blank=True, null=True, help_text="Alternative: Direct link to an externally hosted image.")
    image_alt = models.CharField(max_length=255, blank=True, null=True, help_text="Descriptive text for the category image.")
    icon_svg = models.TextField(blank=True, null=True, help_text="Paste SVG icon code here. Used if provided.")
    
    # Meta / Controls
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Remove')), db_index=True)
    show_on_homepage = models.BooleanField(default=False, verbose_name="Homepage Display", choices=((True, 'Enabled'), (False, 'Disabled')), db_index=True)
    homepage_order   = models.PositiveIntegerField(default=0, verbose_name="Homepage Display Order", db_index=True)
    product_count    = models.PositiveIntegerField(default=0, verbose_name="Cached Product Count", help_text="Denormalized count for performance.")

    # SEO Fields
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Meta Description")
    meta_keywords = models.TextField(blank=True, null=True, verbose_name="Meta Keywords")
    
    @property
    def get_image_url(self):
        if self.image:
            try:
                url = self.image.url
                if url.startswith('/media/media/'):
                    return url.replace('/media/media/', '/media/', 1)
                return url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/512"

    def get_all_children(self, include_self=True):
        """Returns all descendants as model instances using efficient ID fetching."""
        descendant_ids = self.get_descendant_ids(include_self=include_self)
        return Category.objects.filter(id__in=descendant_ids)

    def get_descendant_ids(self, include_self=True, all_cats_prefetched=None):
        """Returns all descendant IDs using a flat fetch of all categories (efficient for small tables)."""
        if all_cats_prefetched is None:
            all_cats_prefetched = Category.objects.filter(is_active=True).values('id', 'parent_id')
            
        children_map = {}
        for c in all_cats_prefetched:
            pid = c['parent_id']
            if pid not in children_map: children_map[pid] = []
            children_map[pid].append(c['id'])
        
        descendants = [self.id] if include_self else []
        stack = list(children_map.get(self.id, []))
        while stack:
            curr_id = stack.pop()
            descendants.append(curr_id)
            if curr_id in children_map:
                stack.extend(children_map[curr_id])
        return descendants

    @property
    def active_subcategories(self):
        return self.subcategories.all()

    def get_ancestors(self, visited=None):
        """Returns ordered list of ancestors from root down to parent."""
        if visited is None: visited = set()
        ancestors = []
        curr = self.parent
        while curr and curr.id not in visited:
            visited.add(curr.id)
            ancestors.insert(0, curr)
            curr = curr.parent
        return ancestors

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.parent:
            curr = self.parent
            while curr:
                if curr == self:
                    raise ValidationError("Circular relationship detected: A category cannot be its own ancestor.")
                curr = curr.parent

    def save(self, *args, **kwargs):
        try:
            self.full_clean()
        except Exception:
            pass # Validation will be handled by the form layer if possible
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        full_path = [self.name]
        k = self.parent
        visited = {self.id}
        while k is not None and k.id not in visited:
            visited.add(k.id)
            full_path.append(k.name)
            k = k.parent
        return ' > '.join(full_path[::-1])

    def get_absolute_url(self):
        from django.urls import reverse
        ancestors = self.get_ancestors()
        if ancestors:
            path = "/".join([a.slug for a in ancestors] + [self.slug])
            return reverse('products:category_hierarchy_detail', kwargs={'hierarchy_path': path})
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    @property
    def total_product_count(self):
        """Returns the denormalized product count."""
        return self.product_count

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['homepage_order', 'name']

# ─── Brand ──────────────────────────────────────────────────────────────────

class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(
        upload_to='brands/', 
        null=True, 
        blank=True,
        help_text="Brand Logo. Recommended: 300x120px. PNG, WEBP."
    )
    logo_url = models.URLField(blank=True, null=True, help_text="Alternative: Direct link to an externally hosted logo.")
    description = models.TextField(blank=True, null=True)
    show_on_homepage = models.BooleanField(default=False, verbose_name="Homepage Display", choices=((True, 'Enabled'), (False, 'Disabled')))
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Remove')))
    order = models.PositiveIntegerField(default=0)

    # SEO Fields
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Meta Description")
    meta_keywords = models.TextField(blank=True, null=True, verbose_name="Meta Keywords")

    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def get_image_url(self):
        if self.logo:
            try:
                url = self.logo.url
                if url.startswith('/media/media/'):
                    return url.replace('/media/media/', '/media/', 1)
                return url
            except (ValueError, AttributeError):
                pass
        if self.logo_url:
            return self.logo_url
        return "https://via.placeholder.com/300x120?text=Brand"

    def __str__(self): return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:brand_detail', kwargs={'slug': self.slug})

# ─── Trust Badge ─────────────────────────────────────────────────────────────

class TrustBadge(models.Model):
    name = models.CharField(max_length=100)
    icon_svg = models.TextField(help_text="Paste SVG icon code here. You can use <a href='https://lucide.dev/icons' target='_blank' style='color:#007bff; font-weight:bold;'>Lucide Icons</a> to find and copy icons.", blank=True)
    background_color = models.CharField(max_length=50, default="#ecfdf5", help_text="e.g., #ecfdf5 (Light green)")
    text_color = models.CharField(max_length=50, default="#065f46", help_text="e.g., #065f46 (Dark green)")
    border_color = models.CharField(max_length=50, default="#d1fae5", help_text="e.g., #d1fae5")
    is_active = models.BooleanField(default=True)

    def __str__(self): return self.name

    class Meta:
        verbose_name = "Trust Badge"
        verbose_name_plural = "Trust Badges"

# ─── Product ─────────────────────────────────────────────────────────────────

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    image = models.ImageField(
        upload_to='products/',
        null=True,
        blank=True,
        help_text="Primary Product Image."
    )
    image_url = models.URLField(blank=True, null=True, help_text="Alternative: Direct link to an externally hosted image.")

    sku_id = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="SKU ID")
    quantity = models.IntegerField(default=0, verbose_name="In-Stock Quantity", db_index=True)
    unit = models.CharField(max_length=20, choices=[('pcs', 'Pieces'), ('box', 'Box'), ('set', 'Set')], default='pcs')

    regular_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    shipping_status = models.CharField(
        max_length=50,
        choices=[('available', 'In Stock'), ('out_of_stock', 'Out of Stock'), ('pre_order', 'Pre-Order')],
        default='available',
        db_index=True
    )
    free_shipping = models.BooleanField(default=False, verbose_name="Free Shipping", choices=((True, 'Enabled'), (False, 'Disabled')))
    additional_shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_time = models.CharField(max_length=100, blank=True, null=True)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, verbose_name="VAT (%)")

    weight = models.FloatField(null=True, blank=True)
    length = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    features = models.TextField(help_text="Key features (one per line)", blank=True, null=True)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5, verbose_name="Average Rating")
    review_count = models.PositiveIntegerField(default=0, verbose_name="Review Count")

    badge = models.CharField(max_length=20, blank=True, null=True, help_text="Small badge text (e.g. NEW, TRENDING)")
    badge_color = models.CharField(max_length=20, default="blue", choices=[
        ("blue", "Blue"), ("red", "Red"), ("green", "Green"), ("dark", "Dark"), ("gold", "Gold")
    ])
    is_featured = models.BooleanField(default=False, verbose_name="Featured Product", db_index=True)

    overview = RichTextField(blank=True, null=True)
    technical_info = RichTextField(blank=True, null=True, verbose_name="Product Characteristics & Specifications")
    shipping_returns = RichTextField(blank=True, null=True, verbose_name="Shipping & Returns Policy")

    trust_badges = models.ManyToManyField(TrustBadge, blank=True, related_name="products")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    show_on_homepage = models.BooleanField(default=False, verbose_name="Homepage Display", choices=((True, 'Enabled'), (False, 'Disabled')), db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Remove')), db_index=True)

    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="Meta Description")
    meta_keywords = models.TextField(blank=True, null=True, verbose_name="Meta Keywords")

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'quantity', 'shipping_status'], name='product_active_qty_status'),
            models.Index(fields=['is_active', 'show_on_homepage'], name='product_active_homepage'),
            models.Index(fields=['category', 'is_active', 'quantity'], name='product_cat_active_qty'),
        ]

    @property
    def features_list(self):
        if not self.features: return []
        return [f.strip() for f in self.features.split('\n') if f.strip()]

    @property
    def get_image_url(self):
        if self.image:
            try:
                url = self.image.url
                if url.startswith('/media/media/'):
                    return url.replace('/media/media/', '/media/', 1)
                return url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/600x400"

    def get_best_price_info(self, prefetched_offers=None):
        if hasattr(self, 'price_info') and prefetched_offers is None:
            return self.price_info
        from django.utils import timezone
        # Safely handle None prices - use Decimal for consistency
        reg = Decimal(str(self.regular_price)) if self.regular_price is not None else Decimal('0.00')
        sale = Decimal(str(self.sale_price)) if self.sale_price is not None else reg

        # Check for active offers
        now = timezone.now()
        
        if prefetched_offers is not None:
            # Filter prefetched offers in memory
            active_offers = []
            ancestor_ids = []
            if self.category:
                # We assume ancestors are already prefetched if needed, or we use the cached parent chain
                curr = self.category
                while curr:
                    ancestor_ids.append(curr.id)
                    curr = curr.parent
            
            for offer in prefetched_offers:
                # Check if offer is active
                if not (offer.start_date <= now <= offer.end_date):
                    continue
                
                # Check if offer applies to this product
                is_applicable = False
                
                # 1. Direct product check
                if hasattr(offer, '_prefetched_products_cache'):
                    if self in offer.products.all():
                        is_applicable = True
                elif offer.products.filter(id=self.id).exists(): # Fallback if not prefetched
                    is_applicable = True
                
                # 2. Category check
                if not is_applicable and ancestor_ids:
                    if hasattr(offer, '_prefetched_categories_cache'):
                        offer_cat_ids = [c.id for c in offer.categories.all()]
                        if any(cat_id in offer_cat_ids for cat_id in ancestor_ids):
                            is_applicable = True
                    elif offer.categories.filter(id__in=ancestor_ids).exists():
                        is_applicable = True
                
                # 3. Brand check
                if not is_applicable and self.brand_id:
                    if hasattr(offer, '_prefetched_brands_cache'):
                        offer_brand_ids = [b.id for b in offer.brands.all()]
                        if self.brand_id in offer_brand_ids:
                            is_applicable = True
                    elif offer.brands.filter(id=self.brand_id).exists():
                        is_applicable = True
                
                if is_applicable:
                    active_offers.append(offer)
        else:
            # 1. Direct Offers
            offers_query = Q(products=self)
            
            # 2. Category Bulk Offers (including ancestors)
            if self.category:
                ancestor_ids = [a.id for a in self.category.get_ancestors()] + [self.category.id]
                offers_query |= Q(categories__id__in=ancestor_ids)
                
            # 3. Brand Bulk Offers
            if self.brand:
                offers_query |= Q(brands=self.brand)

            try:
                active_offers = Offer.objects.filter(
                    offers_query,
                    start_date__lte=now,
                    end_date__gte=now
                ).distinct()
            except Exception:
                active_offers = []

        offer_price = sale
        best_offer_obj = None
        for offer in active_offers:
            current_offer_price = reg
            try:
                discount = Decimal(str(offer.discount_value)) if offer.discount_value else Decimal('0')
                if offer.offer_type == 'percentage':
                    current_offer_price = reg * (1 - (discount / 100))
                elif offer.offer_type == 'fixed':
                    current_offer_price = reg - discount
                elif offer.offer_type == 'final':
                    current_offer_price = discount
            except (TypeError, ValueError, InvalidOperation):
                continue

            if current_offer_price < offer_price:
                offer_price = current_offer_price
                best_offer_obj = offer

        final_price = max(offer_price, Decimal('0'))  # Never go below 0
        discount_amount = reg - final_price
        discount_pct = 0
        if reg > 0:
            discount_pct = (discount_amount / reg) * 100
        ship = Decimal(str(self.additional_shipping_charge)) if (self.additional_shipping_charge is not None and not self.free_shipping) else Decimal('0.00')

        return {
            'has_offer': final_price < reg,
            'final_price': round(final_price, 2),
            'regular_price': round(reg, 2),
            'discount_amount': round(discount_amount, 2),
            'discount_percentage': int(discount_pct),
            'discount_display': f"{int(discount_pct)}% OFF" if final_price < reg else None,
            'shipping_charge': ship,
            'free_shipping': self.free_shipping,
            'total_with_shipping': round(final_price + ship, 2),
            'offer': best_offer_obj,  # The actual Offer object (for cart bogo logic)
            'tabby_payment': round(final_price / 4, 2),
            'tamara_payment': round(final_price / 3, 2),
        }

    @property
    def discount_percentage(self):
        info = self.get_best_price_info()
        return info.get('discount_percentage', 0)

    def is_in_stock(self): return self.quantity > 0 and self.shipping_status == 'available'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            if not self.slug:
                self.slug = "product-" + timezone.now().strftime("%Y%m%d%H%M%S")

        if not self.sku_id:
            prefix = slugify(self.name)[:10].upper() or "PRO"
            unique_id = uuid.uuid4().hex[:8].upper()
            self.sku_id = f"{prefix}-{unique_id}"

        try:
            with transaction.atomic():
                if self.pk is None:
                    existing = Product.objects.filter(sku_id=self.sku_id).select_for_update(nowait=True).exists()
                    if existing:
                        unique_id = uuid.uuid4().hex[:8].upper()
                        self.sku_id = f"{prefix}-{unique_id}"
                super().save(*args, **kwargs)
        except transaction.TransactionManagementError:
            super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    def __str__(self): return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/gallery/', null=True, blank=True)
    image_url = models.URLField(blank=True, null=True)
    image_alt = models.CharField(max_length=255, blank=True, null=True, verbose_name="Alternative Text")
    order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['order']
    def __str__(self):
        return f"Image for {self.product.name}" if self.product else "Unassigned Product Image"
    @property
    def get_image_url(self):
        if self.image:
            try:
                return self.image.url
            except (ValueError, AttributeError):
                pass
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/300"

class Offer(models.Model):
    OFFER_TYPES = (
        ('percentage', 'Percentage Discount (%)'),
        ('fixed', 'Fixed Discount Entry (AED)'),
        ('final', 'Final Set Price (AED)'),
    )
    name = models.CharField(max_length=100)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.ManyToManyField(Product, related_name='offers', blank=True, help_text="Individual product assignment.")
    categories = models.ManyToManyField(Category, related_name='bulk_offers', blank=True, help_text="Apply to all products in these categories (and subcategories).")
    brands = models.ManyToManyField(Brand, related_name='bulk_offers', blank=True, help_text="Apply to all products of these brands.")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    def __str__(self): return self.name

class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    banner = models.ImageField(upload_to='collections/', null=True, blank=True)
    banner_url = models.URLField(blank=True, null=True)
    banner_alt = models.CharField(max_length=255, blank=True, null=True)
    products = models.ManyToManyField(Product, related_name='collections', blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True, verbose_name="Status", choices=((True, 'Active'), (False, 'Remove')))
    layout = models.CharField(max_length=20, default='3_col', choices=[
        ('1_col', '1-Image (Full Width)'),
        ('2_col', '2-Images (50% Width)'),
        ('3_col', '3-Images (33% Width)'),
    ], help_text="Determine the visual size of this collection on the homepage grid.")
    
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('products:collection_detail', kwargs={'slug': self.slug})
    def __str__(self): return self.name

    @property
    def get_image_url(self):
        if self.banner:
            try:
                return self.banner.url
            except (ValueError, AttributeError):
                pass
        if self.banner_url:
            return self.banner_url
        return "https://via.placeholder.com/1200x400?text=Collection"

    class Meta: ordering = ['display_order']

class Wishlist(models.Model):
    from django.conf import settings
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
