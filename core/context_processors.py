from django.utils import timezone
from django.db.models import Q, Sum
from .models import SiteSettings, AnnouncementBar
from .design_models import DesignSettings
from products.models import Product
from orders.models import CustomerOrder
from contact.models import ContactFormSubmission
from blog.models import Post

from django.core.cache import cache

SITE_SETTINGS_CACHE_KEY = 'site_wide_settings_v1'

def invalidate_site_settings_cache():
    """Clear the cached site settings. Call this when SiteSettings or DesignSettings are updated."""
    cache.delete(SITE_SETTINGS_CACHE_KEY)

def site_settings(request):
    """
    Cached site-wide settings and announcements.
    """
    # Use a versioned cache key based on DesignSettings updated_at for immediate reflection
    # This ensures that after saving in admin, the next request automatically gets fresh data
    design_version = "v1"
    try:
        latest_design = DesignSettings.objects.only('updated_at', 'id').first()
        if latest_design and latest_design.updated_at:
            design_version = f"v1_{int(latest_design.updated_at.timestamp())}"
    except Exception:
        pass

    versioned_key = f"{SITE_SETTINGS_CACHE_KEY}_{design_version}"
    data = cache.get(versioned_key)
    
    if data is None:
        try:
            # Ensure a SiteSettings record always exists (singleton pattern)
            settings, created = SiteSettings.objects.get_or_create(
                id=1,
                defaults={
                    'site_name': 'JKR International',
                    'meta_title': 'JKR International | Advanced Medical Equipment',
                    'meta_description': 'Precision medical technology and healthcare equipment for hospitals and clinics worldwide.',
                }
            )

            now = timezone.now()
            announcements = list(AnnouncementBar.objects.filter(is_active=True).filter(
                Q(start_date__isnull=True) | Q(start_date__lte=now)
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=now)
            ).order_by('id'))
            
            # Ensure DesignSettings also always exists
            design, _ = DesignSettings.objects.get_or_create(id=1)
            latest_posts = list(Post.objects.filter(is_published=True).order_by('-created_at')[:3])
            
            data = {
                'site_settings': settings,
                'design_settings': design,
                'announcement_bar_list': announcements,
                'latest_blog_posts': latest_posts,
            }
            # Cache for 5 minutes (signal invalidation + versioned key makes it near real-time)
            cache.set(versioned_key, data, 300)
        except Exception:
            # Fallback with safe dummy objects
            dummy_site = SiteSettings(site_name="Site", meta_title="Site")
            dummy_design = DesignSettings()
            return {
                'site_settings': dummy_site,
                'design_settings': dummy_design,
                'announcement_bar_list': [],
                'latest_blog_posts': [],
            }
            
    return data

def page_heroes(request):
    from pages.models import PageHero
    try:
        # Get existing heroes
        db_heroes = {hero.page: hero for hero in PageHero.objects.filter(is_active=True)}
        
        # Ensure all choices have an object (even if unsaved)
        heroes = {}
        for choice_key, choice_label in PageHero.PAGE_CHOICES:
            if choice_key in db_heroes:
                heroes[choice_key] = db_heroes[choice_key]
            else:
                # Return an unsaved instance with the page set
                # This allows templates to call .display_title etc.
                heroes[choice_key] = PageHero(page=choice_key, is_active=True)
                
    except Exception:
        heroes = {}
        
    return {
        'page_heroes': heroes,
    }


def admin_dashboard(request):
    """Provides key metrics for the admin dashboard summary."""
    if not request.path.startswith('/admin/'):
        return {}
    
    try:
        total_orders = CustomerOrder.objects.count()
        total_revenue = CustomerOrder.objects.filter(payment_status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_products = Product.objects.count()
        new_messages = ContactFormSubmission.objects.filter(is_read=False).count()
        
        return {
            'dashboard_summary': {
                'orders': total_orders,
                'revenue': f"{total_revenue:,.2f}",
                'products': total_products,
                'messages': new_messages
            }
        }
    except Exception:
        return {}
