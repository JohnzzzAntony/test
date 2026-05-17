from django.db import models
from django.conf import settings
from products.models import Product


# ─── Legacy Order (kept for compatibility) ────────────────────────────────────

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


# ─── Quote Enquiry ────────────────────────────────────────────────────────────

class QuoteEnquiry(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    department = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255, blank=True)
    street2 = models.CharField(max_length=255, blank=True, verbose_name="Street Address 2")
    emirates = models.CharField(max_length=100, blank=True, verbose_name="Emirate/State")
    phone = models.CharField(max_length=50)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, default='New', choices=(
        ('New', 'New'),
        ('Processing', 'Processing'),
        ('Quoted', 'Quoted'),
        ('Closed', 'Closed'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enquiry from {self.first_name} {self.last_name} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Quote Enquiry"
        verbose_name_plural = "Quote Enquiries"


class QuoteItem(models.Model):
    enquiry = models.ForeignKey(QuoteEnquiry, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ─── Customer Order (full checkout flow) ──────────────────────────────────────

class CustomerOrder(models.Model):

    PAYMENT_METHOD_CHOICES = (
        ('card',   'Credit / Debit Card'),
        ('tabby',  'Tabby – Pay in 4'),
        ('tamara', 'Tamara – Pay in 3'),
        ('cod',    'Cash on Delivery'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    )

    ORDER_STATUS_CHOICES = (
        ('pending',           'Pending'),
        ('packaging',         'Packaging'),
        ('ready_for_shipment', 'Ready for shipment'),
        ('shipped',           'Shipped'),
        ('delivered',         'Delivered'),
        ('return_to_origin',   'Return to origin'),
        ('refund',            'Refund'),
    )

    EMIRATES_CHOICES = (
        ('Abu Dhabi', 'Abu Dhabi'),
        ('Dubai', 'Dubai'),
        ('Sharjah', 'Sharjah'),
        ('Ajman', 'Ajman'),
        ('Umm Al Quwain', 'Umm Al Quwain'),
        ('Ras Al Khaimah', 'Ras Al Khaimah'),
        ('Fujairah', 'Fujairah'),
    )

    # ── Billing / Customer ──────────────────────────────────────────────────
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    is_guest    = models.BooleanField(default=False)
    
    # Shipping Address (Primary)
    first_name  = models.CharField(max_length=100)
    last_name   = models.CharField(max_length=100)
    email       = models.EmailField()
    phone       = models.CharField(max_length=50)
    department  = models.CharField(max_length=255, blank=True)
    country     = models.CharField(max_length=100)
    city        = models.CharField(max_length=100)
    street      = models.CharField(max_length=255, blank=True)
    street2     = models.CharField(max_length=255, blank=True, verbose_name="Street Address 2")
    emirates    = models.CharField(max_length=50, choices=EMIRATES_CHOICES, default='Dubai')
    comment     = models.TextField(blank=True, verbose_name="Customer Notes")

    # TRN (Tax Registration Number)
    trn = models.CharField(
        max_length=15, 
        blank=True, 
        null=True, 
        verbose_name="TRN Number", 
        help_text="UAE TRN (exactly 15 digits)"
    )

    # Billing Address (Separate)
    billing_address_same_as_shipping = models.BooleanField(default=True)
    billing_first_name = models.CharField(max_length=100, blank=True)
    billing_last_name = models.CharField(max_length=100, blank=True)
    billing_email = models.EmailField(blank=True)
    billing_phone = models.CharField(max_length=50, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_street = models.CharField(max_length=255, blank=True)
    billing_street2 = models.CharField(max_length=255, blank=True, verbose_name="Billing Street Address 2")
    billing_emirates = models.CharField(max_length=50, choices=EMIRATES_CHOICES, blank=True)

    # ── Payment ─────────────────────────────────────────────────────────────
    payment_method  = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cod')
    payment_status  = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)

    # ── Order Management ─────────────────────────────────────────────────────
    status          = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='pending', verbose_name="Order Status")
    
    # Financial Breakdown
    coupon_code     = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total promotional discount")
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total shipping cost for this order")
    tax_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total tax amount for this order")
    total_amount    = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Grand Total (Items - Discount + Shipping + Tax)")
    
    admin_notes     = models.TextField(blank=True, verbose_name="Internal Admin Notes")
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Customer Order"
        verbose_name_plural = "Customer Orders"
        indexes = [
            models.Index(fields=['user', '-created_at'], name='order_user_created'),
            models.Index(fields=['payment_status', 'status'], name='order_payment_status'),
            models.Index(fields=['email', '-created_at'], name='order_email_created'),
            models.Index(fields=['stripe_session_id'], name='order_stripe_session'),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status

    def __str__(self):
        return f"Order #{self.pk} — {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def compute_total(self):
        items_total = sum(item.total_price for item in self.items.all())
        # Tax is typically calculated on the discounted subtotal + shipping
        taxable_amount = items_total - self.discount_amount + self.shipping_amount
        self.tax_amount = (taxable_amount * 5 / 100) # Default 5% VAT if not specified otherwise
        self.total_amount = taxable_amount + self.tax_amount
        self.save(update_fields=['total_amount', 'tax_amount'])
        return self.total_amount

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        status_changed = not is_new and self.status != self.__status

        super().save(*args, **kwargs)

        if is_new or status_changed:
            # 1. Log history
            OrderStatusHistory.objects.create(order=self, status=self.status)

            # 2. Trigger notifications
            from .notifications import send_customer_notification
            if is_new:
                send_customer_notification(self, notification_type='order_placed')
            else:
                send_customer_notification(self, notification_type='status_change')

            self.__status = self.status


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(CustomerOrder, related_name='history', on_delete=models.CASCADE)
    status = models.CharField(max_length=30)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name = "Order Status History"
        verbose_name_plural = "Order Status Histories"

    def __str__(self):
        return f"{self.order} — {self.status} at {self.changed_at}"


class CustomerOrderItem(models.Model):
    order        = models.ForeignKey(CustomerOrder, related_name='items', on_delete=models.CASCADE)
    product      = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, help_text="Snapshot of name at time of order")
    quantity     = models.PositiveIntegerField(default=1)
    regular_price   = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Regular price before offer")
    offer_price     = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Site price at time of order")
    unit_price      = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Final price after item discounts")
    tax_percentage  = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="VAT percentage at time of order")
    tax_amount      = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Tax amount for this item")
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Shipping cost for this specific item")
    total_price     = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        # Calculate tax from percentage
        if self.tax_percentage:
            self.tax_amount = (self.total_price * self.tax_percentage) / 100
        else:
            self.tax_amount = 0

        if self.product and not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
