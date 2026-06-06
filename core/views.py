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
    """Homepage view rendering the premium homepage"""
    from pages.models import HomepageSettings
    homepage_settings = HomepageSettings.get_settings()
    
    context = {
        'homepage_settings': homepage_settings,
        'categories': Category.objects.filter(is_active=True),
        'featured_products': Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8],
        'latest_products': Product.objects.filter(is_active=True).order_by('-created_at').select_related('category')[:8],
    }
    return render(request, '21st_home.html', context)

def about_us_view(request):
    """Specific About Us page."""
    about_us = AboutUs.objects.first()
    mission = MissionVision.objects.filter(section_type='mission').first()
    vision = MissionVision.objects.filter(section_type='vision').first()
    counters = Counter.objects.filter(is_active=True).order_by('order')
    
    from pages.models import WhyUsCard
    from products.models import Category
    why_us = WhyUsCard.objects.filter(is_active=True).order_by('order')
    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('homepage_order', 'name')[:8]
    
    return render(request, 'pages/about.html', {
        'about_us': about_us,
        'mission': mission,
        'vision': vision,
        'counters': counters,
        'why_us': why_us,
        'categories': categories,
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


def newsletter_subscribe(request):
    """Handle newsletter subscription form (AJAX or standard POST)."""
    if request.method != 'POST':
        from django.shortcuts import redirect
        return redirect('core:home')

    email = request.POST.get('email', '').strip()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if not email or '@' not in email:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Invalid email address'}, status=400)
        from django.shortcuts import redirect
        return redirect('core:home')

    try:
        from .models import NewsletterSubscription
        obj, created = NewsletterSubscription.objects.get_or_create(email=email)
        if is_ajax:
            return JsonResponse({'success': True, 'created': created})
    except Exception:
        # If model doesn't exist yet, silently accept
        if is_ajax:
            return JsonResponse({'success': True, 'created': True})

    from django.shortcuts import redirect
    return redirect('core:home')

def privacy_policy_view(request):
    """Privacy Policy Page."""
    return render(request, 'pages/privacy_policy.html', {})

def terms_conditions_view(request):
    """Terms and Conditions Page."""
    return render(request, 'pages/terms_conditions.html', {})
