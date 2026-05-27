from django.contrib import admin, messages
from django.utils.html import mark_safe, format_html
from django.conf import settings
from django.db.models import Q
from .models import CustomerOrder, CustomerOrderItem, OrderStatusHistory, QuoteEnquiry, QuoteItem
from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from import_export.widgets import ForeignKeyWidget
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.utils import timezone
from datetime import timedelta

# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_order_rank(order):
    """
    Returns the 1-based order count for a customer identified by email OR phone.
    """
    ids = list(
        CustomerOrder.objects.filter(
            Q(email__iexact=order.email) | Q(phone=order.phone)
        ).order_by('created_at').values_list('id', flat=True)
    )
    try:
        return ids.index(order.id) + 1
    except ValueError:
        return 1


def _badge(label, color):
    return mark_safe(
        f'<span style="background:{color};color:#fff;padding:3px 10px;'
        f'border-radius:12px;font-size:11px;font-weight:700;white-space:nowrap;">{label}</span>'
    )


# ─── Status colour maps ───────────────────────────────────────────────────────

ORDER_STATUS_COLORS = {
    'pending':            '#ffc107',
    'packaging':          '#fd7e14',
    'ready_for_shipment': '#007bff',
    'shipped':            '#6f42c1',
    'delivered':          '#28a745',
    'return_to_origin':    '#e83e8c',
    'refund':             '#dc3545',
}

PAYMENT_STATUS_COLORS = {
    'pending':  '#ffc107',
    'paid':     '#28a745',
    'failed':   '#dc3545',
    'refunded': '#6c757d',
}

PAYMENT_METHOD_ICONS = {
    'card':   '💳',
    'tabby':  '🟢',
    'tamara': '🟠',
    'cod':    '💵',
}


# ─── Customer Order Items Inline ───────────────────────────────────────────────

class CustomerOrderItemInline(admin.TabularInline):
    model = CustomerOrderItem
    extra = 0
    fields = ('product', 'product_name', 'quantity', 'regular_price', 'offer_price', 'unit_price', 'shipping_charge', 'total_price')
    readonly_fields = ('total_price',)

    def has_add_permission(self, request, obj=None):
        return True


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('status_badge', 'changed_at')
    can_delete = False
    
    def status_badge(self, obj):
        color = ORDER_STATUS_COLORS.get(obj.status, '#888')
        label = dict(CustomerOrder.ORDER_STATUS_CHOICES).get(obj.status, obj.status)
        return _badge(label, color)
    status_badge.short_description = "Status"

    def has_add_permission(self, request, obj=None):
        return False


# ─── Custom Filters ───────────────────────────────────────────────────────────

class CreatedAtRangeFilter(admin.SimpleListFilter):
    title = 'date ordered'
    parameter_name = 'created_at_custom'

    def lookups(self, request, model_admin):
        return (
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('7_days', 'Past 7 days'),
            ('30_days', 'Past 30 days'),
            ('this_month', 'This Month'),
            ('custom', 'Custom Range'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        
        now = timezone.now().date()
        if val == 'today':
            return queryset.filter(created_at__date=now)
        if val == 'yesterday':
            return queryset.filter(created_at__date=now - timedelta(days=1))
        if val == '7_days':
            return queryset.filter(created_at__date__gte=now - timedelta(days=7))
        if val == '30_days':
            return queryset.filter(created_at__date__gte=now - timedelta(days=30))
        if val == 'this_month':
            return queryset.filter(created_at__year=now.year, created_at__month=now.month)
        return queryset


# ─── Export Resource ──────────────────────────────────────────────────────────

class CustomerOrderResource(resources.ModelResource):
    order_number = fields.Field(column_name='Order #')
    user_name = fields.Field(attribute='user', column_name='User', widget=ForeignKeyWidget(settings.AUTH_USER_MODEL, 'username'))
    guest_flag = fields.Field(attribute='is_guest', column_name='Is Guest')
    loyalty_tag = fields.Field(column_name='Loyalty Tag')
    full_name = fields.Field(column_name='Customer Name')
    email = fields.Field(attribute='email', column_name='Email')
    phone = fields.Field(attribute='phone', column_name='Phone')
    trn = fields.Field(attribute='trn', column_name='TRN')
    payment_method_display = fields.Field(column_name='Payment Method')
    payment_status_display = fields.Field(column_name='Payment Status')
    order_status_display = fields.Field(column_name='Order Status')
    items_summary = fields.Field(column_name='Items')
    total_with_currency = fields.Field(column_name='Total')
    date_created = fields.Field(column_name='Created At')

    class Meta:
        model = CustomerOrder
        fields = (
            'order_number', 'user_name', 'guest_flag', 'loyalty_tag', 
            'full_name', 'email', 'phone', 'trn', 'payment_method_display', 
            'payment_status_display', 'order_status_display', 
            'items_summary', 'total_with_currency', 'date_created'
        )
        export_order = (
            'order_number', 'user_name', 'guest_flag', 'loyalty_tag', 
            'full_name', 'email', 'phone', 'trn', 'payment_method_display', 
            'payment_status_display', 'order_status_display', 
            'items_summary', 'total_with_currency', 'date_created'
        )

    def dehydrate_order_number(self, obj):
        return f"#Demo-{obj.pk:05d}"

    def dehydrate_loyalty_tag(self, obj):
        rank = get_order_rank(obj)
        return "New" if rank == 1 else f"Repeat {rank}"

    def dehydrate_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def dehydrate_payment_method_display(self, obj):
        return obj.get_payment_method_display()

    def dehydrate_payment_status_display(self, obj):
        return obj.get_payment_status_display()

    def dehydrate_order_status_display(self, obj):
        return obj.get_status_display()

    def dehydrate_items_summary(self, obj):
        return ", ".join([f"{item.product_name} (x{item.quantity})" for item in obj.items.all()])

    def dehydrate_total_with_currency(self, obj):
        return f"{obj.total_amount} {settings.CURRENCY}"

    def dehydrate_date_created(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M")


# ─── Customer Order ────────────────────────────────────────────────────────────

@admin.register(CustomerOrder)
class CustomerOrderAdmin(ImportExportModelAdmin):
    resource_class = CustomerOrderResource
    actions = ['export_as_pdf']
    
    list_display  = (
        'order_number', 
        'user', 
        'is_guest', 
        'customer_tag',
        'customer_name', 
        'email', 
        'phone',
        'payment_method_badge', 
        'payment_status_badge',
        'status',
        'items_count', 
        'total_display',
        'created_at',
    )
    list_editable = ('status',) 
    list_filter   = (
        'status', 
        'payment_method', 
        'payment_status', 
        'country', 
        CreatedAtRangeFilter,
    )
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'id')
    readonly_fields = (
        'order_number', 'created_at', 'updated_at',
        'items_total_display',
        'customer_order_tag', 
        'resend_notification_button',
        'print_invoice_buttons',
        'tax_amount',
    )
    inlines = [CustomerOrderItemInline, OrderStatusHistoryInline]

    # ── Custom Methods ───────────────────────────────────────────────────────

    def print_invoice_buttons(self, obj):
        if not obj.pk: return "-"
        from django.urls import reverse
        try:
            print_url = reverse('admin:order-print', args=[obj.pk])
            invoice_url = reverse('admin:order-invoice', args=[obj.pk])
        except Exception:
            return "Error: Custom admin URLs not registered."
        return format_html(
            '<div style="display:flex; gap:12px;">'
            '<a class="button btn-warning" href="{}" target="_blank" style="background:#ea580c; color:white; padding:10px 25px; font-weight:700; border-radius:12px; transition:0.2s;">'
            '<i class="fas fa-print"></i> Order Print</a>'
            '<a class="button btn-primary" href="{}" target="_blank" style="background:#2563eb; color:white; padding:10px 25px; font-weight:700; border-radius:12px; transition:0.2s;">'
            '<i class="fas fa-file-invoice"></i> Order Invoice</a>'
            '</div>',
            print_url, invoice_url
        )
    print_invoice_buttons.short_description = "Order Documents"

    def customer_tag(self, obj):
        rank = get_order_rank(obj)
        if rank == 1:
            return _badge("New", "#28a745")
        return _badge(f"Repeat {rank}", "#007bff")
    customer_tag.short_description = "Loyalty"

    def customer_order_tag(self, obj):
        rank = get_order_rank(obj)
        label = "First Time Order" if rank == 1 else f"Returning Customer (Order #{rank})"
        badge = self.customer_tag(obj)
        return format_html('{} <span style="margin-left:10px;font-size:13px;color:#666;">{}</span>', badge, label)
    customer_order_tag.short_description = "Loyalty Status"

    def order_number(self, obj):
        if not obj.pk: return "#NEW"
        return format_html('<strong>#Demo-{}</strong>', f"{obj.pk:05d}")
    order_number.short_description = "Order #"
    order_number.admin_order_field = 'id'

    def customer_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    customer_name.short_description = "Customer"

    def payment_method_badge(self, obj):
        icon = PAYMENT_METHOD_ICONS.get(obj.payment_method, '💳')
        label = obj.get_payment_method_display()
        return format_html('<span style="font-size:13px;">{} {}</span>', icon, label)
    payment_method_badge.short_description = "Payment"

    def payment_status_badge(self, obj):
        color = PAYMENT_STATUS_COLORS.get(obj.payment_status, '#888')
        return _badge(obj.get_payment_status_display(), color)
    payment_status_badge.short_description = "Payment Status"

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Items"

    def total_display(self, obj):
        return format_html('<strong>{} {}</strong>', obj.total_amount, settings.CURRENCY)
    total_display.short_description = "Total"

    def resend_notification_button(self, obj):
        if not obj.pk: return "-"
        from django.urls import reverse
        url = reverse('admin:resend-notification', args=[obj.pk])
        return format_html(
            '<div style="margin-top:5px;">'
            '<a class="button btn btn-primary" href="{}" style="padding:4px 12px; font-size:12px;">'
            '📨 Resend Notifications</a>'
            '</div>',
            url
        )
    resend_notification_button.short_description = "Notifications"

    def get_product_price(self, request):
        from django.http import JsonResponse
        from products.models import Product
        product_id = request.GET.get('product_id')
        if not product_id:
            return JsonResponse({'error': 'No product_id provided'}, status=400)
        try:
            product = Product.objects.get(id=product_id)
            price_info = product.get_best_price_info()
            
            # Use Product fields directly instead of missing 'skus' attribute
            shipping_charge = 0 if product.free_shipping else (product.additional_shipping_charge or 0)
            
            return JsonResponse({
                'unit_price': float(price_info['final_price']),
                'shipping_charge': float(shipping_charge),
                'product_name': product.name
            })
        except Exception as e:
            return JsonResponse({'error': f"Price Error: {str(e)}"}, status=500)

    def items_total_display(self, obj):
        from django.utils.html import format_html_join
        items = list(obj.items.all())  # Materialize once — avoids double DB query
        rows = format_html_join(
            '',
            '<tr><td style="padding:8px 10px;">{}</td>'
            '<td style="padding:8px 10px;text-align:center;">{}</td>'
            '<td style="padding:8px 10px;text-align:right;">{} {}</td>'
            '<td style="padding:8px 10px;text-align:right;">{} {}</td>'
            '<td style="padding:8px 10px;text-align:right;">{} {}</td>'
            '<td style="padding:8px 10px;text-align:right;font-weight:700;">{} {}</td></tr>',
            ((i.product_name, i.quantity, i.regular_price, settings.CURRENCY, i.offer_price, settings.CURRENCY, i.unit_price, settings.CURRENCY, i.total_price, settings.CURRENCY) for i in items)
        )
        items_subtotal = sum(i.total_price for i in items)
        return format_html(
            '<table style="width:100%; border-collapse:collapse; font-size:13px; border:1px solid #eee; border-radius:8px; overflow:hidden;">'
            '<thead><tr style="background:#f8fafc; border-bottom:1px solid #eee;">'
            '<th style="padding:10px; text-align:left;">Product</th>'
            '<th style="padding:10px; text-align:center;">Qty</th>'
            '<th style="padding:10px; text-align:right;">Regular</th>'
            '<th style="padding:10px; text-align:right;">Offer</th>'
            '<th style="padding:10px; text-align:right;">Final</th>'
            '<th style="padding:10px; text-align:right;">Subtotal</th></tr></thead>'
            '<tbody>{}</tbody>'
            '<tfoot>'
            '<tr style="background:#fafafa;"><td colspan="5" style="padding:10px; text-align:right; color:#64748b;">Items Subtotal</td>'
            '<td style="padding:10px; text-align:right; color:#64748b;">{} {}</td></tr>'
            '<tr style="background:#fafafa;"><td colspan="5" style="padding:10px; text-align:right; color:#f43f5e;">Coupon Discount ({})</td>'
            '<td style="padding:10px; text-align:right; color:#f43f5e;">- {} {}</td></tr>'
            '<tr style="background:#fafafa;"><td colspan="5" style="padding:10px; text-align:right; color:#64748b;">Shipping</td>'
            '<td style="padding:10px; text-align:right; color:#64748b;">{} {}</td></tr>'
            '<tr style="background:#fafafa;"><td colspan="5" style="padding:10px; text-align:right; color:#64748b;">VAT (Tax)</td>'
            '<td style="padding:10px; text-align:right; color:#64748b;">{} {}</td></tr>'
            '<tr style="background:#f1f5f9; font-weight:700; font-size:15px;"><td colspan="5" style="padding:12px 10px; text-align:right;">Grand Total</td>'
            '<td style="padding:12px 10px; text-align:right; color:#2563eb;">{} {}</td></tr>'
            '</tfoot>'
            '</table>',
            mark_safe(rows),
            items_subtotal, settings.CURRENCY,
            obj.coupon_code or "None", obj.discount_amount or 0, settings.CURRENCY,
            obj.shipping_amount or 0, settings.CURRENCY,
            obj.tax_amount or 0, settings.CURRENCY,
            obj.total_amount or 0, settings.CURRENCY
        )
    items_total_display.short_description = "Detailed Summary"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/resend-notification/', self.admin_site.admin_view(self.resend_notification), name='resend-notification'),
            path('<int:order_id>/print/', self.admin_site.admin_view(self.print_order), name='order-print'),
            path('<int:order_id>/invoice/', self.admin_site.admin_view(self.generate_invoice), name='order-invoice'),
            path('ajax/get-product-price/', self.admin_site.admin_view(self.get_product_price), name='ajax-get-product-price'),
        ]
        return custom_urls + urls

    def resend_notification(self, request, order_id):
        from .notifications import send_customer_notification
        from django.shortcuts import get_object_or_404, redirect
        order = get_object_or_404(CustomerOrder, pk=order_id)
        send_customer_notification(order, is_automated=False)
        self.message_user(request, f"Notifications have been successfully resent for Order #Demo-{order_id:05d}.")
        return redirect('admin:orders_customerorder_change', order_id)

    def print_order(self, request, order_id):
        from django.shortcuts import get_object_or_404, render
        order = get_object_or_404(CustomerOrder, pk=order_id)
        site_name = settings.DEMO_SITE_NAME if hasattr(settings, 'DEMO_SITE_NAME') else "Demo International"
        return render(request, 'admin/orders/print_order.html', {
            'order': order,
            'site_name': site_name,
            'currency': getattr(settings, 'CURRENCY', 'AED'),
        })

    def generate_invoice(self, request, order_id):
        from django.shortcuts import get_object_or_404
        from .utils import create_invoice_pdf
        order = get_object_or_404(CustomerOrder, pk=order_id)
        return create_invoice_pdf(order)

    # ── Fieldsets ────────────────────────────────────────────────────────────

    fieldsets = (
        ('Order Identification', {
            'fields': ('order_number', 'customer_order_tag', 'trn'),
        }),
        ('Documents', {
            'fields': ('print_invoice_buttons',),
        }),
        ('Customer Details', {
            'fields': (
                'first_name', 
                'last_name',
                'email', 
                'phone',
                'department', 
                'user', 
                'is_guest',
            ),
        }),
        ('Shipping Address', {
            'fields': (
                'country', 
                'city',
                'street',
                'comment',
            ),
        }),
        ('Billing Address', {
            'classes': ('collapse',),
            'fields': (
                'billing_address_same_as_shipping',
                'billing_first_name', 
                'billing_last_name',
                'billing_email', 
                'billing_phone',
                'billing_country', 
                'billing_city',
                'billing_street',
            ),
        }),
        ('Payment & Financials', {
            'fields': (
                'payment_method', 
                'payment_status',
                'coupon_code', 
                'discount_amount',
                'shipping_amount', 
                'tax_amount', 
                'total_amount',
            ),
        }),
        ('Order Processing', {
            'fields': (
                'status',
                'resend_notification_button',
                'admin_notes',
                'created_at', 
                'updated_at',
            ),
        }),
        ('Items Summary Board', {
            'fields': ('items_total_display',),
        }),
    )

    class Media:
        css = {'all': ('admin/css/admin_orders.css',)}
        js = ('admin/js/admin_orders.js',)

    @admin.action(description="Export Selected Orders as PDF")
    def export_as_pdf(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="orders_export_{timezone.now().strftime("%Y%m%d")}.pdf"'
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Customer Orders Export — {timezone.now().strftime('%Y-%m-%d')}", styles['Title']))
        elements.append(Paragraph("<br/>", styles['Normal']))
        
        # Optimized column widths for landscape A4
        col_widths = [0.8*inch, 0.7*inch, 1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.9*inch, 0.5*inch, 1.1*inch, 0.9*inch]
        
        data = [['Order #', 'Loyalty', 'Customer', 'Email', 'Pay Method', 'Pay Status', 'Status', 'Qty', 'Total', 'Date']]
        resource = self.resource_class()
        
        inner_style = ParagraphStyle('inner', parent=styles['Normal'], fontSize=8, leading=10)
        
        from django.utils.html import escape
        for obj in queryset:
            # Wrap potentially long strings in Paragraphs and escape for safety
            customer_p = Paragraph(escape(resource.dehydrate_full_name(obj)), inner_style)
            email_p = Paragraph(escape(obj.email), inner_style)
            
            data.append([
                resource.dehydrate_order_number(obj),
                resource.dehydrate_loyalty_tag(obj),
                customer_p,
                email_p,
                obj.get_payment_method_display()[:6],
                obj.get_payment_status_display(),
                obj.get_status_display(),
                str(obj.items.count()),
                resource.dehydrate_total_with_currency(obj),
                obj.created_at.strftime("%y-%m-%d")
            ])
            
        table = Table(data, repeatRows=1, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#114084")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(table)
        doc.build(elements)
        return response


# ─── Quote Enquiry Admin ──────────────────────────────────────────────────────

class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    fields = ('product', 'quantity')

@admin.register(QuoteEnquiry)
class QuoteEnquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'department', 'status', 'created_at')
    list_filter = ('status', 'country', 'city')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    list_editable = ('status',)
    inlines = [QuoteItemInline]
    readonly_fields = ('created_at',)
