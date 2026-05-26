"""
21st Century Healthcare - Premium Frontend Views
================================================
Views for the new premium design system.
Import these into your main urls.py
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from products.models import Product, Category, Brand
from orders.models import Order, CartItem
from accounts.models import User


def home_21st(request):
    """Premium homepage view"""
    context = {
        'categories': Category.objects.filter(is_active=True).annotate(product_count=Count('products')),
        'featured_products': Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8],
        'latest_products': Product.objects.filter(is_active=True).order_by('-created_at').select_related('category')[:8],
        'cart_count': request.session.get('cart_count', 0),
        'wishlist_count': 0,
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
        'categories': Category.objects.filter(is_active=True).annotate(product_count=Count('products')),
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

    context = {
        'product': product,
        'related_products': related,
        'cart_count': request.session.get('cart_count', 0),
    }
    return render(request, '21st_product_detail.html', context)


def cart_21st(request):
    """Premium cart view"""
    # Get cart from session
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product', 'product__category')
    else:
        cart_items = []

    subtotal = sum(item.total_item for item in cart_items)
    total = subtotal  # Add shipping/discount logic as needed

    context = {
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'cart_total': total,
        'cart_count': len(cart_items) if cart_items else 0,
    }
    return render(request, '21st_cart.html', context)


def checkout_21st(request):
    """Premium checkout view"""
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
    else:
        cart_items = []

    subtotal = sum(item.total_item for item in cart_items)
    total = subtotal

    context = {
        'step': request.GET.get('step', 'billing'),
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'cart_total': total,
    }
    return render(request, '21st_checkout.html', context)


# Admin Views
@login_required
def admin_dashboard_21st(request):
    """Admin dashboard overview"""
    return render(request, '21st_admin_dashboard.html')


@login_required
def admin_products_21st(request):
    """Admin product list"""
    products = Product.objects.all().select_related('category')
    return render(request, '21st_admin_products.html', {'products': products})


@login_required
def admin_orders_21st(request):
    """Admin order list"""
    return render(request, '21st_admin_orders.html')


@login_required
def admin_customers_21st(request):
    """Admin customer list"""
    customers = User.objects.filter(is_active=True)
    return render(request, '21st_admin_customers.html', {'customers': customers})


@login_required
def admin_inventory_21st(request):
    """Admin inventory management"""
    products = Product.objects.all().select_related('category')
    return render(request, '21st_admin_inventory.html', {'products': products})
