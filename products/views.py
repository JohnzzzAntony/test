from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max, F
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from .models import Product, Category, ProductImage, Wishlist, Brand, Collection, Offer

@staff_member_required
def delete_product_media(request, pk):
    """Instantly deletes a ProductImage and its physical file via AJAX."""
    if request.method == 'POST':
        try:
            image_obj = get_object_or_404(ProductImage, pk=pk)
            if image_obj.image:
                image_obj.image.delete(save=False)
            image_obj.delete()
            return JsonResponse({'status': 'success', 'message': 'Gallery image deleted permanently.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@staff_member_required
def clear_primary_product_image(request, pk):
    """Instantly clears the main image field of a Product via AJAX."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=pk)
            if product.image:
                # Use storage delete to ensure Cloudinary/S3 file is removed
                product.image.delete(save=False)
                product.image = None
                product.save(update_fields=['image'])
            return JsonResponse({'status': 'success', 'message': 'Primary image cleared permanently.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@login_required
def wishlist_view(request):
    """Displays the user's favorited products."""
    from django.utils import timezone
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product').prefetch_related(
        'product__images', 'product__category', 'product__brand'
    ).order_by('-added_at')
    
    # Pre-fetch all active offers once
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    products = []
    for item in wishlist_items:
        p = item.product
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)
        products.append(p)
    
    return render(request, 'products/wishlist.html', {
        'products': products
    })

@login_required
def toggle_wishlist(request, product_id):
    """Toggles a product in the user's wishlist via AJAX."""
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, pk=product_id)
            wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
            
            if not created:
                wishlist_item.delete()
                # Get updated count
                count = Wishlist.objects.filter(user=request.user).count()
                return JsonResponse({'status': 'removed', 'count': count, 'message': 'Removed from wishlist.'})
            
            count = Wishlist.objects.filter(user=request.user).count()
            return JsonResponse({'status': 'added', 'id': product.id, 'count': count, 'message': 'Added to wishlist!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

@staff_member_required
def get_subcategories(request, parent_id):
    """Returns a list of subcategories for a given parent ID as JSON."""
    subcategories = Category.objects.filter(parent_id=parent_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)

def category_index(request):
    """Shows top-level categories in a professional grid."""
    categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
    if not categories.exists():
        categories = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    return render(request, 'products/category_index.html', {'categories': categories})

def product_list(request):
    """Shows all products with stock, and categories in sidebar."""
    from django.utils import timezone
    parents = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
    categories = parents if parents.count() > 1 else Category.objects.filter(is_active=True).prefetch_related('subcategories')

    # Pre-fetch all active offers once to avoid N+1 in price calculation
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    # Base Queryset
    products = Product.objects.filter(
        is_active=True,
        quantity__gt=0,
        shipping_status='available'
    ).select_related('category', 'brand').prefetch_related(
        'images'
    ).annotate(
        effective_price=Coalesce('sale_price', 'regular_price')
    ).distinct()

    # Filter by active offers if on_sale=1 is passed
    on_sale = request.GET.get('on_sale')
    if on_sale == '1':
        products = products.filter(
            Q(offers__start_date__lte=now, offers__end_date__gte=now) |
            Q(sale_price__isnull=False, sale_price__lt=F('regular_price'))
        ).distinct()
    
    # Calculate global price bounds for the filter UI
    price_bounds = products.aggregate(
        min_p=Min('effective_price'),
        max_p=Max('effective_price')
    )
    
    # Text Search
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(overview__icontains=query) | Q(sku_id__icontains=query)
        )

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: products = products.filter(effective_price__gte=min_price)
        except: pass
    if max_price:
        try: products = products.filter(effective_price__lte=max_price)
        except: pass

    # Brand Filtering
    selected_brands = request.GET.getlist('brands')
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)
    
    # Rating Filtering
    min_rating = request.GET.get('rating')
    if min_rating:
        try: products = products.filter(avg_rating__gte=min_rating)
        except: pass

    # Sorting Logic
    sort = request.GET.get('sort', '-id')
    if sort == 'price_low':
        products = products.order_by('effective_price')
    elif sort == 'price_high':
        products = products.order_by('-effective_price')
    elif sort == 'name_az':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attach price info in-memory using prefetched offers
    for p in page_obj:
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)
    
    return render(request, 'products/product_list.html', {
        'categories': categories,
        'products': page_obj,
        'current_sort': sort,
        'all_brands': Brand.objects.filter(is_active=True).order_by('order', 'name'),
        'all_brands_count': Brand.objects.filter(is_active=True).count(),
        'price_bounds': price_bounds,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'selected_brands': [int(b) for b in selected_brands if b.isdigit()],
            'min_rating': min_rating,
        }
    })

def category_detail(request, slug=None, hierarchy_path=None):
    """
    Highly advanced SEO-friendly category view that supports absolute paths.
    """
    from django.utils import timezone
    if hierarchy_path:
        slug = hierarchy_path.strip('/').split('/')[-1]
    
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    cat_ids = category.get_descendant_ids(include_self=True)

    # Pre-fetch all active offers once
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    # Base Queryset
    products = Product.objects.filter(
        category_id__in=cat_ids,
        is_active=True,
        quantity__gt=0,
        shipping_status='available'
    ).select_related('category', 'brand').prefetch_related(
        'images'
    ).annotate(
        effective_price=Coalesce('sale_price', 'regular_price')
    ).distinct()

    # Calculate global price bounds for the filter UI
    price_bounds = products.aggregate(
        min_p=Min('effective_price'),
        max_p=Max('effective_price')
    )

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: products = products.filter(effective_price__gte=min_price)
        except: pass
    if max_price:
        try: products = products.filter(effective_price__lte=max_price)
        except: pass

    # Brand Filtering
    selected_brands = request.GET.getlist('brands')
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)
    
    # Rating Filtering
    min_rating = request.GET.get('rating')
    if min_rating:
        try: products = products.filter(avg_rating__gte=min_rating)
        except: pass

    # Sorting Logic
    sort = request.GET.get('sort', '-id')
    if sort == 'price_low':
        products = products.order_by('effective_price')
    elif sort == 'price_high':
        products = products.order_by('-effective_price')
    elif sort == 'name_az':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attach price info
    for p in page_obj:
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)
    
    # Root categories for sidebar
    roots = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')

    return render(request, 'products/product_list.html', {
        'current_category': category, 
        'products': page_obj,
        'categories': roots,
        'ancestors': category.get_ancestors(),
        'current_sort': sort,
        'all_brands': Brand.objects.filter(is_active=True).order_by('order', 'name'),
        'all_brands_count': Brand.objects.filter(is_active=True).count(),
        'price_bounds': price_bounds,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'selected_brands': [int(b) for b in selected_brands if b.isdigit()],
            'min_rating': min_rating,
        }
    })

from core.design_models import DesignSettings

def product_detail(request, slug=None, pk=None):
    """SEO-friendly product detail page. Supports both slug and PK for administrative legacy tools."""
    from django.utils import timezone
    if pk:
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand').prefetch_related('images'), 
            pk=pk, is_active=True
        )
    else:
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand').prefetch_related('images'), 
            slug=slug, is_active=True
        )

    # Pre-fetch all active offers once
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))
    
    product.price_info = product.get_best_price_info(prefetched_offers=active_offers)

    # Fetch related products from the same category
    design = DesignSettings.objects.first()
    related_count = design.pd_related_count if design else 4
    
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        quantity__gt=0
    ).exclude(id=product.id).select_related('category', 'brand').prefetch_related('images')[:related_count]

    for p in related_products:
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products
    })


# ── REST API For Category Management ───────────────────────────────────────────
try:
    from rest_framework import viewsets, permissions, status
    from rest_framework.response import Response
    from rest_framework.decorators import action
    from .serializers import CategoryTreeSerializer, CategoryDetailSerializer
    _DRF_AVAILABLE = True
except ImportError:
    _DRF_AVAILABLE = False

class CategoryViewSet(viewsets.ModelViewSet):
    """
    Comprehensive API for Category CRUD and Hierarchical Tree Management.
    """
    queryset = Category.objects.all().select_related('parent').prefetch_related('subcategories')
    serializer_class = CategoryDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    @action(detail=False, methods=['get'], url_path='tree')
    def get_tree(self, request):
        """Returns the nested category tree structure."""
        roots = self.get_queryset().filter(parent__isnull=True)
        serializer = CategoryTreeSerializer(roots, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='products')
    def get_products(self, request, slug=None):
        """Returns products specifically for this category and all its subcategories."""
        category = self.get_object()
        all_cat_ids = [c.id for c in category.get_all_children(include_self=True)]
        
        from .serializers import ProductListSerializer 
        products = Product.objects.filter(category_id__in=all_cat_ids)
        return Response(ProductListSerializer(products, many=True).data)

    def destroy(self, request, *args, **kwargs):
        """Handle children properly - logic is in on_delete=CASCADE in models.py"""
        return super().destroy(request, *args, **kwargs)

def collection_detail(request, slug):
    """
    Shows products belonging to a specific collection.
    """
    from django.utils import timezone
    collection = get_object_or_404(Collection, slug=slug, is_active=True)
    
    # Pre-fetch all active offers once
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    # Base Queryset
    products = collection.products.filter(
        is_active=True,
        quantity__gt=0,
        shipping_status='available'
    ).select_related('category', 'brand').prefetch_related(
        'images'
    ).annotate(
        effective_price=Coalesce('sale_price', 'regular_price')
    ).distinct()

    # Calculate global price bounds for the filter UI
    price_bounds = products.aggregate(
        min_p=Min('effective_price'),
        max_p=Max('effective_price')
    )

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: products = products.filter(effective_price__gte=min_price)
        except: pass
    if max_price:
        try: products = products.filter(effective_price__lte=max_price)
        except: pass

    # Brand Filtering
    selected_brands = request.GET.getlist('brands')
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)
    
    # Rating Filtering
    min_rating = request.GET.get('rating')
    if min_rating:
        try: products = products.filter(avg_rating__gte=min_rating)
        except: pass

    # Sorting Logic
    sort = request.GET.get('sort', '-id')
    if sort == 'price_low':
        products = products.order_by('effective_price')
    elif sort == 'price_high':
        products = products.order_by('-effective_price')
    elif sort == 'name_az':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attach price info
    for p in page_obj:
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)
    
    # Root categories for sidebar
    roots = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')

    return render(request, 'products/product_list.html', {
        'collection': collection, 
        'products': page_obj,
        'categories': roots,
        'title': collection.name,
        'current_sort': sort,
        'all_brands': Brand.objects.filter(is_active=True).order_by('order', 'name'),
        'all_brands_count': Brand.objects.filter(is_active=True).count(),
        'price_bounds': price_bounds,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'selected_brands': [int(b) for b in selected_brands if b.isdigit()],
            'min_rating': min_rating,
        }
    })

def brand_list(request):
    """Shows all active brands."""
    brands = Brand.objects.filter(is_active=True)
    return render(request, 'products/brand_list.html', {'brands': brands})

def brand_detail(request, slug):
    """Shows products for a specific brand."""
    from django.utils import timezone
    brand = get_object_or_404(Brand, slug=slug, is_active=True)

    # Pre-fetch all active offers once
    now = timezone.now()
    active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    # Base Queryset
    products = Product.objects.filter(
        brand=brand,
        is_active=True,
        quantity__gt=0,
        shipping_status='available'
    ).select_related('category', 'brand').prefetch_related(
        'images'
    ).annotate(
        effective_price=Coalesce('sale_price', 'regular_price')
    ).distinct()

    # Calculate global price bounds for the filter UI
    price_bounds = products.aggregate(
        min_p=Min('effective_price'),
        max_p=Max('effective_price')
    )

    # Price Filtering
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: products = products.filter(effective_price__gte=min_price)
        except: pass
    if max_price:
        try: products = products.filter(effective_price__lte=max_price)
        except: pass

    # No need to filter by brand ID since we are already in brand detail
    # But for consistency with the template which might show other brand filters:
    selected_brands = request.GET.getlist('brands')
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)
    
    # Rating Filtering
    min_rating = request.GET.get('rating')
    if min_rating:
        try: products = products.filter(avg_rating__gte=min_rating)
        except: pass

    # Sorting Logic
    sort = request.GET.get('sort', '-id')
    if sort == 'price_low':
        products = products.order_by('effective_price')
    elif sort == 'price_high':
        products = products.order_by('-effective_price')
    elif sort == 'name_az':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-id')

    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Attach price info
    for p in page_obj:
        p.price_info = p.get_best_price_info(prefetched_offers=active_offers)
    
    roots = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('subcategories')
    
    return render(request, 'products/product_list.html', {
        'current_brand': brand,
        'products': page_obj,
        'categories': roots,
        'title': f"Products by {brand.name}",
        'current_sort': sort,
        'all_brands': Brand.objects.filter(is_active=True).order_by('order', 'name'),
        'all_brands_count': Brand.objects.filter(is_active=True).count(),
        'price_bounds': price_bounds,
        'current_filters': {
            'min_price': min_price,
            'max_price': max_price,
            'selected_brands': [int(b) for b in selected_brands if b.isdigit()],
            'min_rating': min_rating,
        }
    })


def collection_list(request):
    """Shows all active collections."""
    collections = Collection.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'products/collection_list.html', {'collections': collections})
