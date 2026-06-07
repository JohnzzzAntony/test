"""
21st Century Healthcare - Premium Frontend Views
================================================
Views for the new premium design system.
Import these into your main urls.py
"""

import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, F, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from products.models import Product, Category, Brand, Offer
from orders.models import CustomerOrder, CustomerOrderItem, OrderStatusHistory
from core.models import NewsletterSubscription, SocialPost, Testimonial, StoreLocation, AnnouncementBar

def home_21st(request):
    """Premium homepage view"""
    context = {
        'categories': Category.objects.filter(is_active=True),
        'featured_products': Product.objects.filter(is_active=True, exclusive_products=True).select_related('category')[:8],
        'latest_products': Product.objects.filter(is_active=True).order_by('-created_at').select_related('category')[:8],
        'cart_count': request.session.get('cart_count', 0),
    }
    return render(request, '21st_home.html', context)


def product_list_21st(request):
    """Premium product listing view"""
    from django.core.paginator import Paginator

    products_list = Product.objects.filter(is_active=True).select_related('category')
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'categories': Category.objects.filter(is_active=True),
        'current_category': None,
        'cart_count': request.session.get('cart_count', 0),
    }
    return render(request, '21st_product_list.html', context)


def product_detail_21st(request, slug):
    """Premium product detail view"""
    product = get_object_or_404(Product.objects.select_related('category', 'brand'), slug=slug)
    related = Product.objects.filter(
        is_active=True,
        category=product.category
    ).exclude(id=product.id).select_related('category')[:4]

    # Mock data for template compatibility
    product.total_reviews = 0

    context = {
        'product': product,
        'related_products': related,
        'cart_count': request.session.get('cart_count', 0),
    }
    return render(request, '21st_product_detail.html', context)


def cart_21st(request):
    """Premium cart view"""
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    cart_items = []
    total = Decimal('0.00')
    for product_id, item_data in cart.items():
        if isinstance(item_data, dict):
            quantity = item_data.get('quantity', 1)
        else:
            quantity = int(item_data)
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            price_info = product.get_best_price_info()
            final_price = Decimal(str(price_info['final_price']))
            item_total = final_price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_item': item_total,
            })
        except Product.DoesNotExist:
            pass

    context = {
        'cart_items': cart_items,
        'cart_subtotal': total,
        'cart_total': total,
        'cart_count': sum(item['quantity'] for item in cart_items),
    }
    return render(request, '21st_cart.html', context)


def checkout_21st(request):
    """Premium checkout view"""
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    cart_items = []
    total = Decimal('0.00')
    for product_id, item_data in cart.items():
        if isinstance(item_data, dict):
            quantity = item_data.get('quantity', 1)
        else:
            quantity = int(item_data)
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            price_info = product.get_best_price_info()
            final_price = Decimal(str(price_info['final_price']))
            item_total = final_price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_item': item_total,
            })
        except Product.DoesNotExist:
            pass

    context = {
        'step': request.GET.get('step', 'billing'),
        'cart_items': cart_items,
        'cart_subtotal': total,
        'cart_total': total,
    }
    return render(request, '21st_checkout.html', context)


# ==========================================
# 21st Century Admin Dashboard Views
# ==========================================

@staff_member_required(login_url='accounts:login')
def admin_dashboard_21st(request):
    """Admin dashboard overview with dynamic calculations and serialized chart inputs"""
    User = get_user_model()
    
    # KPIs
    products_count = Product.objects.count()
    orders_count = CustomerOrder.objects.count()
    customers_count = User.objects.filter(is_active=True).count()
    low_stock_items = Product.objects.filter(quantity__lte=10).count()
    
    # Total Revenue (only paid orders)
    revenue_agg = CustomerOrder.objects.filter(payment_status='paid').aggregate(total_rev=Sum('total_amount'))
    total_revenue = revenue_agg['total_rev'] or Decimal('0.00')
    
    # Recent Orders
    recent_orders = CustomerOrder.objects.all().select_related('user').order_by('-created_at')[:5]
    
    # Top Products by sales count (from CustomerOrderItem for paid orders)
    top_products_list = Product.objects.filter(
        customerorderitem__order__payment_status='paid'
    ).annotate(
        sales_count=Sum('customerorderitem__quantity')
    ).order_by('-sales_count')[:5]
    
    # Chart 1: Revenue by month (Current Year)
    current_year = timezone.now().year
    monthly_revenue = [0] * 12
    for m in range(12):
        month_start = timezone.datetime(current_year, m + 1, 1, tzinfo=timezone.get_current_timezone())
        if m == 11:
            month_end = timezone.datetime(current_year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
        else:
            month_end = timezone.datetime(current_year, m + 2, 1, tzinfo=timezone.get_current_timezone())
            
        month_rev = CustomerOrder.objects.filter(
            payment_status='paid',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        monthly_revenue[m] = float(month_rev)
        
    # Chart 2: Sales by Category
    category_sales = Category.objects.filter(
        products__customerorderitem__order__payment_status='paid'
    ).annotate(
        units_sold=Sum('products__customerorderitem__quantity')
    ).order_by('-units_sold')[:5]
    
    category_labels = [cat.name for cat in category_sales]
    category_data = [int(cat.units_sold) for cat in category_sales]
    
    # Chart 3: Orders by Status
    status_counts = CustomerOrder.objects.values('status').annotate(count=Count('id'))
    status_data_dict = {item['status']: item['count'] for item in status_counts}
    
    status_labels = ['pending', 'packaging', 'ready_for_shipment', 'shipped', 'delivered', 'refund', 'return_to_origin']
    status_data = [status_data_dict.get(s, 0) for s in status_labels]

    context = {
        'products_count': products_count,
        'orders_count': orders_count,
        'customers_count': customers_count,
        'low_stock_items': low_stock_items,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'top_products_list': top_products_list,
        'monthly_revenue_json': json.dumps(monthly_revenue),
        'category_labels_json': json.dumps(category_labels),
        'category_data_json': json.dumps(category_data),
        'status_labels_json': json.dumps([s.replace('_', ' ').capitalize() for s in status_labels]),
        'status_data_json': json.dumps(status_data),
    }
    return render(request, '21st_admin_dashboard.html', context)


@staff_member_required(login_url='accounts:login')
def admin_products_21st(request, pk=None):
    """Admin product list with AJAX toggle/delete operations"""
    from django.core.paginator import Paginator
    
    # Intercept API calls
    if request.path.endswith('/delete/') and request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return JsonResponse({'success': True, 'message': 'Product deleted successfully.'})
        
    if request.path.endswith('/toggle/') and request.method == 'POST':
        product = get_object_or_404(Product, pk=pk)
        product.is_active = not product.is_active
        product.save()
        return JsonResponse({'success': True, 'is_active': product.is_active})

    search_query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    
    products_list = Product.objects.all().select_related('category').order_by('-id')
    if search_query:
        products_list = products_list.filter(Q(name__icontains=search_query) | Q(sku_id__icontains=search_query))
    if category_id:
        products_list = products_list.filter(category_id=category_id)
        
    paginator = Paginator(products_list, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': int(category_id) if category_id.isdigit() else None,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_products.html', context)


@staff_member_required(login_url='accounts:login')
def admin_orders_21st(request, pk=None):
    """Admin order list with status updates and AJAX filtering"""
    from django.core.paginator import Paginator
    
    # Intercept API status update
    if request.path.endswith('/status/') and request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_status = data.get('status')
            order = get_object_or_404(CustomerOrder, pk=pk)
            if new_status in dict(CustomerOrder.ORDER_STATUS_CHOICES):
                order.status = new_status
                order.save()
                return JsonResponse({'success': True, 'message': f'Order status updated to {new_status}.'})
            return JsonResponse({'success': False, 'error': 'Invalid status choice.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    selected_status = request.GET.get('status', 'all').strip()
    search_query = request.GET.get('q', '').strip()
    
    orders_list = CustomerOrder.objects.all().select_related('user').order_by('-created_at')
    
    if selected_status != 'all':
        orders_list = orders_list.filter(status=selected_status)
    if search_query:
        orders_list = orders_list.filter(Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query) | Q(id__icontains=search_query))
        
    paginator = Paginator(orders_list, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        'selected_status': selected_status,
        'search_query': search_query,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_orders.html', context)


@staff_member_required(login_url='accounts:login')
def admin_customers_21st(request):
    """Admin customer list populated from User model with spent annotations"""
    from django.core.paginator import Paginator
    User = get_user_model()
    
    search_query = request.GET.get('q', '').strip()
    
    customers_list = User.objects.filter(is_active=True).annotate(
        orders_qty=Count('orders', distinct=True),
        spent_amount=Sum('orders__total_amount')
    ).order_by('-id')
    
    if search_query:
        customers_list = customers_list.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) | 
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query)
        )
        
    paginator = Paginator(customers_list, 20)
    page_number = request.GET.get('page')
    customers = paginator.get_page(page_number)
    
    context = {
        'customers': customers,
        'search_query': search_query,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_customers.html', context)


@staff_member_required(login_url='accounts:login')
def admin_inventory_21st(request, pk=None):
    """Admin inventory management with AJAX stock replenishment updates"""
    from django.core.paginator import Paginator
    
    if request.path.endswith('/adjust/') and request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_qty = int(data.get('quantity', 0))
            product = get_object_or_404(Product, pk=pk)
            product.quantity = max(0, new_qty)
            if product.quantity == 0:
                product.shipping_status = 'out_of_stock'
            else:
                product.shipping_status = 'available'
            product.save()
            return JsonResponse({'success': True, 'quantity': product.quantity, 'shipping_status': product.get_shipping_status_display()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    selected_status = request.GET.get('status', 'all').strip()
    search_query = request.GET.get('q', '').strip()
    
    products_list = Product.objects.all().select_related('category').order_by('quantity')
    
    if selected_status == 'in_stock':
        products_list = products_list.filter(quantity__gt=10)
    elif selected_status == 'low_stock':
        products_list = products_list.filter(quantity__gt=0, quantity__lte=10)
    elif selected_status == 'out_of_stock':
        products_list = products_list.filter(quantity=0)
        
    if search_query:
        products_list = products_list.filter(Q(name__icontains=search_query) | Q(sku_id__icontains=search_query))
        
    paginator = Paginator(products_list, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    low_stock_count = Product.objects.filter(quantity__lte=10).count()
    
    context = {
        'products': products,
        'low_stock_count': low_stock_count,
        'selected_status': selected_status,
        'search_query': search_query,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_inventory.html', context)


# ==========================================
# Additional Admin Views for Core Modules
# ==========================================

@staff_member_required(login_url='accounts:login')
def admin_newsletter_21st(request, pk=None):
    """Admin newsletter subscriptions list with subscriber delete action"""
    from django.core.paginator import Paginator
    
    if request.path.endswith('/delete/') and request.method == 'POST':
        sub = get_object_or_404(NewsletterSubscription, pk=pk)
        sub.delete()
        return JsonResponse({'success': True, 'message': 'Subscriber removed successfully.'})

    search_query = request.GET.get('q', '').strip()
    subscriptions_list = NewsletterSubscription.objects.all().order_by('-subscribed_at')
    
    if search_query:
        subscriptions_list = subscriptions_list.filter(email__icontains=search_query)
        
    paginator = Paginator(subscriptions_list, 20)
    page_number = request.GET.get('page')
    subscriptions = paginator.get_page(page_number)
    
    context = {
        'subscriptions': subscriptions,
        'search_query': search_query,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_newsletter.html', context)


@staff_member_required(login_url='accounts:login')
def admin_social_21st(request):
    """Admin social posts management"""
    from django.core.paginator import Paginator
    
    if request.method == 'POST' and request.path.endswith('/action/'):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            post_id = data.get('id')
            if action == 'delete':
                post = get_object_or_404(SocialPost, pk=post_id)
                post.delete()
                return JsonResponse({'success': True})
            elif action == 'create':
                post = SocialPost.objects.create(
                    link=data.get('link', ''),
                    image_url=data.get('image_url', 'https://via.placeholder.com/400'),
                    image_alt=data.get('image_alt', ''),
                    order=data.get('order', 0)
                )
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    posts_list = SocialPost.objects.all().order_by('order')
    paginator = Paginator(posts_list, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_social.html', context)


@staff_member_required(login_url='accounts:login')
def admin_testimonials_21st(request):
    """Admin testimonials management"""
    from django.core.paginator import Paginator
    
    if request.method == 'POST' and request.path.endswith('/action/'):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            t_id = data.get('id')
            if action == 'delete':
                t = get_object_or_404(Testimonial, pk=t_id)
                t.delete()
                return JsonResponse({'success': True})
            elif action == 'toggle_status':
                t = get_object_or_404(Testimonial, pk=t_id)
                t.is_active = not t.is_active
                t.save()
                return JsonResponse({'success': True, 'is_active': t.is_active})
            elif action == 'create':
                t = Testimonial.objects.create(
                    client_name=data.get('client_name'),
                    position=data.get('position', ''),
                    content=data.get('content', ''),
                    rating=int(data.get('rating', 5)),
                    order=int(data.get('order', 0)),
                    is_active=True
                )
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    testimonials_list = Testimonial.objects.all().order_by('order')
    paginator = Paginator(testimonials_list, 20)
    page_number = request.GET.get('page')
    testimonials = paginator.get_page(page_number)
    
    context = {
        'testimonials': testimonials,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_testimonials.html', context)


@staff_member_required(login_url='accounts:login')
def admin_locations_21st(request):
    """Admin store locations management"""
    from django.core.paginator import Paginator
    
    if request.method == 'POST' and request.path.endswith('/action/'):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            l_id = data.get('id')
            if action == 'delete':
                loc = get_object_or_404(StoreLocation, pk=l_id)
                loc.delete()
                return JsonResponse({'success': True})
            elif action == 'toggle_status':
                loc = get_object_or_404(StoreLocation, pk=l_id)
                loc.is_active = not loc.is_active
                loc.save()
                return JsonResponse({'success': True, 'is_active': loc.is_active})
            elif action == 'create':
                loc = StoreLocation.objects.create(
                    name=data.get('name'),
                    city=data.get('city'),
                    address=data.get('address'),
                    phone=data.get('phone'),
                    map_url=data.get('map_url', ''),
                    is_active=True,
                    order=int(data.get('order', 0))
                )
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    locations_list = StoreLocation.objects.all().order_by('order')
    paginator = Paginator(locations_list, 20)
    page_number = request.GET.get('page')
    locations = paginator.get_page(page_number)
    
    context = {
        'locations': locations,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_locations.html', context)


@staff_member_required(login_url='accounts:login')
def admin_announcements_21st(request):
    """Admin announcement bar management"""
    from django.core.paginator import Paginator
    
    if request.method == 'POST' and request.path.endswith('/action/'):
        try:
            data = json.loads(request.body)
            action = data.get('action')
            a_id = data.get('id')
            if action == 'delete':
                ann = get_object_or_404(AnnouncementBar, pk=a_id)
                ann.delete()
                return JsonResponse({'success': True})
            elif action == 'toggle_status':
                ann = get_object_or_404(AnnouncementBar, pk=a_id)
                ann.is_active = not ann.is_active
                ann.save()
                return JsonResponse({'success': True, 'is_active': ann.is_active})
            elif action == 'create':
                ann = AnnouncementBar.objects.create(
                    text=data.get('text'),
                    background_color=data.get('background_color', '#000000'),
                    text_color=data.get('text_color', '#ffffff'),
                    closable=data.get('closable', True),
                    is_active=True
                )
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    announcements_list = AnnouncementBar.objects.all().order_by('-is_active', 'id')
    paginator = Paginator(announcements_list, 20)
    page_number = request.GET.get('page')
    announcements = paginator.get_page(page_number)
    
    context = {
        'announcements': announcements,
        'products_count': Product.objects.count(),
        'orders_count': CustomerOrder.objects.count(),
    }
    return render(request, '21st_admin_announcements.html', context)
