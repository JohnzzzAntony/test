from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import SiteSettings, Testimonial, Client, SocialPost, StoreLocation
from django.db import models
from products.models import Category, Product, Collection, Brand, Offer
from sliders.models import HeroSlider, PromoBanner
from pages.models import AboutUs, MissionVision, Service, Counter, WhyUsCard, Partner, GalleryItem, HomepageSettings, HeroSlide
from .models import Testimonial, Client, SocialPost, StoreLocation

class MockCategory:
    def __init__(self, slug, name):
        self.slug = slug
        self.name = name
    @property
    def get_image_url(self):
        return None
    def get_absolute_url(self):
        from django.urls import reverse
        try:
            return reverse('products:category_detail', kwargs={'slug': self.slug})
        except Exception:
            return f"/products/category/{self.slug}/"

def home(request):
    """Homepage aggregation view."""
    # Hero image slides (right panel)
    hero_slides = HeroSlide.objects.filter(is_active=True).order_by('order')

    # Homepage text / toggle settings (singleton)
    hp_settings = HomepageSettings.get_settings()

    sliders = HeroSlider.objects.filter(is_active=True).order_by('order')

    # Promo Banners / Promo Sections from admin (sliders app)
    promo_sections = PromoBanner.objects.filter(is_active=True).prefetch_related('items').order_by('homepage_order')

    # Categories for homepage - top-level only (no parent)
    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('homepage_order', 'name')[:12]

    # Specific 8 shop-by-categories in exact order
    category_slugs = [
        ('wheelchairs', 'Wheelchairs'),
        ('walking-standing-aids', 'Walking & Standing Aids'),
        ('seating-positioning-system', 'Seating & Positioning Systems'),
        ('prosthetics-orthotics-services', 'Prosthetics & Orthotics Services'),
        ('physiotherapy-rehabilitation-product', 'Physiotherapy & Rehabilitation Products'),
        ('orthopedic-products', 'Orthopedic Products'),
        ('hospital-equipment-furniture', 'Hospital Equipment & Furniture'),
        ('homecare', 'Homecare')
    ]
    db_cats = {c.slug: c for c in Category.objects.filter(slug__in=[s[0] for s in category_slugs], is_active=True)}
    shop_by_categories = []
    for slug, default_name in category_slugs:
        if slug in db_cats:
            shop_by_categories.append(db_cats[slug])
        else:
            shop_by_categories.append(MockCategory(slug, default_name))

    about_us = AboutUs.objects.filter(is_active=True).first()
    
    # Batch Mission/Vision queries to reduce one round-trip
    mv_sections = MissionVision.objects.filter(section_type__in=['mission', 'vision'], is_active=True)
    mission = next((mv for mv in mv_sections if mv.section_type == 'mission'), None)
    vision = next((mv for mv in mv_sections if mv.section_type == 'vision'), None)
    
    services = Service.objects.filter(is_active=True).order_by('order')
    counters = Counter.objects.filter(is_active=True).order_by('order')
    why_us = WhyUsCard.objects.filter(is_active=True).order_by('order')
    partners = Partner.objects.filter(is_active=True).order_by('order')
    gallery = GalleryItem.objects.filter(is_active=True).order_by('order')[:8]
    
    testimonials = Testimonial.objects.filter(is_active=True).order_by('order')
    public_clients = Client.objects.filter(category='Public', is_active=True).order_by('order')
    private_clients = Client.objects.filter(category='Private', is_active=True).order_by('order')
    social_posts = SocialPost.objects.all().order_by('order')[:6]
    
    # Optimized latest_products (fallback)
    latest_products = Product.objects.filter(
        quantity__gt=0,
        is_active=True
    ).select_related('category', 'brand').prefetch_related('offers', 'images').order_by('-id')[:8]

    # Fetch Products with active offers (either via Offer model or manual sale_price)
    now = timezone.now()
    active_offers_products = Product.objects.filter(
        is_active=True,
        quantity__gt=0,
    ).filter(
        models.Q(offers__start_date__lte=now, offers__end_date__gte=now) |
        models.Q(sale_price__isnull=False, sale_price__lt=models.F('regular_price'))
    ).distinct().select_related('category', 'brand').prefetch_related('offers', 'images')

    # Featured Products - Only products explicitly marked as featured via admin
    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True,
        quantity__gt=0
    ).select_related('category', 'brand').prefetch_related('offers', 'images').order_by('-id')
    
    # Pre-fetch all active offers for price calculation optimization
    all_active_offers = list(Offer.objects.filter(
        start_date__lte=now,
        end_date__gte=now
    ).prefetch_related('products', 'categories', 'brands'))

    # Helper to attach price info in bulk to avoid N+1 in templates
    def attach_price_info(product_list):
        for p in product_list:
            p.price_info = p.get_best_price_info(prefetched_offers=all_active_offers)
            
    attach_price_info(latest_products)
    attach_price_info(featured_products)
    attach_price_info(active_offers_products)

    # Homepage Collections: Filter active ones and prefetch related Products.
    collections = Collection.objects.filter(is_active=True).prefetch_related(
        'products', 
        'products__category',
        'products__brand',
        'products__offers',
        'products__images'
    )
    for col in collections:
        attach_price_info(col.products.all())

    brands = Brand.objects.filter(show_on_homepage=True, is_active=True).order_by('order')

    context = {
        'hp_settings': hp_settings,
        'hero_slides': hero_slides,
        'sliders': sliders,
        'promo_sections': promo_sections,
        'categories': categories,
        'shop_by_categories': shop_by_categories,
        'collections': collections,
        'active_offers_products': active_offers_products,
        'about_us': about_us,
        'mission_vision': [mv for mv in [mission, vision] if mv],
        'services': services,
        'counters': counters,
        'why_us': why_us,
        'partners': partners,
        'gallery': gallery,
        'testimonials': testimonials,
        'public_clients': public_clients,
        'private_clients': private_clients,
        'social_posts': social_posts,
        'latest_products': latest_products,
        'featured_products': featured_products,
        'brands': brands,
    }
    return render(request, 'index.html', context)

def about_us_view(request):
    """Specific About Us page."""
    about_us = AboutUs.objects.first()
    mission = MissionVision.objects.filter(section_type='mission').first()
    vision = MissionVision.objects.filter(section_type='vision').first()
    counters = Counter.objects.filter(is_active=True).order_by('order')
    return render(request, 'pages/about.html', {
        'about_us': about_us,
        'mission': mission,
        'vision': vision,
        'counters': counters
    })

def services_view(request):
    """Specific Services page."""
    services = Service.objects.all().order_by('order')
    return render(request, 'pages/services.html', {'services': services})

def gallery_view(request):
    """Specific Gallery page."""
    gallery = GalleryItem.objects.all().order_by('order')
    return render(request, 'pages/gallery.html', {'gallery': gallery})

def store_locations_view(request):
    """Store Locations page with server-side city filtering and pagination."""
    selected_city = request.GET.get('city', 'all')
    stores_qs = StoreLocation.objects.all().order_by('order', 'name')
    
    if selected_city != 'all':
        stores_qs = stores_qs.filter(city=selected_city)
    
    paginator = Paginator(stores_qs, 9) # 9 stores per page (3x3 grid)
    page_number = request.GET.get('page')
    stores = paginator.get_page(page_number)
    
    cities = StoreLocation.objects.all().values_list('city', flat=True).distinct().order_by('city')
    
    return render(request, 'pages/stores.html', {
        'stores': stores,
        'cities': cities,
        'selected_city': selected_city
    })
def health_check(request):
    """Simple health check endpoint for monitoring."""
    return JsonResponse({'status': 'healthy', 'timestamp': timezone.now().isoformat()})

def faq_view(request):
    """FAQ / Help Center page."""
    return render(request, 'pages/faq.html', {})

def shipping_info_view(request):
    """Shipping & Delivery Information page."""
    return render(request, 'pages/shipping.html', {})
def robots_txt_view(request):
    """Serve dynamic robots.txt content from SiteSettings."""
    settings = SiteSettings.objects.first()
    content = ""
    if settings and settings.robots_txt:
        content = settings.robots_txt
    else:
        content = "User-agent: *\nDisallow: /admin/\nDisallow: /checkout/\nAllow: /"
    
    return HttpResponse(content, content_type="text/plain")
