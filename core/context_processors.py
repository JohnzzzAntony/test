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
    Cached site-wide settings, announcements, and global nav data.
    """
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

            design, _ = DesignSettings.objects.get_or_create(id=1)
            latest_posts = list(Post.objects.filter(is_published=True).order_by('-created_at')[:3])

            # Nav-level querysets for header mega-menu (all templates)
            try:
                from products.models import Brand, Collection, Offer
                nav_brands = list(Brand.objects.filter(is_active=True).order_by('order')[:10])
                nav_collections = list(Collection.objects.filter(is_active=True).order_by('display_order')[:10])
                nav_offers = list(Offer.objects.filter(
                    start_date__lte=now, end_date__gte=now
                )[:6])
            except Exception:
                nav_brands = []
                nav_collections = []
                nav_offers = []

            data = {
                'site_settings': settings,
                'design_settings': design,
                'announcement_bar_list': announcements,
                'latest_blog_posts': latest_posts,
                'nav_brands': nav_brands,
                'nav_collections': nav_collections,
                'nav_offers': nav_offers,
            }
            cache.set(versioned_key, data, 300)
        except Exception:
            dummy_site = SiteSettings(site_name="Site", meta_title="Site")
            dummy_design = DesignSettings()
            return {
                'site_settings': dummy_site,
                'design_settings': dummy_design,
                'announcement_bar_list': [],
                'latest_blog_posts': [],
                'nav_brands': [],
                'nav_collections': [],
                'nav_offers': [],
            }

    return data

def page_heroes(request):
    from pages.models import PageHero
    try:
        db_heroes = {hero.page: hero for hero in PageHero.objects.filter(is_active=True)}
        heroes = {}
        for choice_key, choice_label in PageHero.PAGE_CHOICES:
            if choice_key in db_heroes:
                heroes[choice_key] = db_heroes[choice_key]
            else:
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
