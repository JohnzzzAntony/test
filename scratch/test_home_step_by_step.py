import os
import sys
import django
import time

sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')

django.setup()

from django.test import RequestFactory, override_settings
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils import timezone
from django.db import models

# Import models
from core.models import SiteSettings, Testimonial, Client, SocialPost, StoreLocation
from products.models import Category, Product, Collection, Brand, Offer
from sliders.models import HeroSlider, PromoBanner
from pages.models import AboutUs, MissionVision, Service, Counter, WhyUsCard, Partner, GalleryItem, HomepageSettings, HeroSlide
from core.views import MockCategory

class DummySession(dict):
    pass

@override_settings(CACHES={
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "jkr-test-override",
    }
})
def run_diagnostic():
    print("--- Starting step-by-step view execution ---")
    
    start = time.time()
    
    print("1. Querying HeroSlide...")
    hero_slides = list(HeroSlide.objects.filter(is_active=True).order_by('order'))
    print(f"   Done: {len(hero_slides)} slides in {time.time() - start:.2f}s")
    
    start = time.time()
    print("2. Querying HomepageSettings...")
    hp_settings = HomepageSettings.get_settings()
    print(f"   Done in {time.time() - start:.2f}s")
    
    start = time.time()
    print("3. Querying HeroSlider...")
    sliders = list(HeroSlider.objects.filter(is_active=True).order_by('order'))
    print(f"   Done: {len(sliders)} sliders in {time.time() - start:.2f}s")
    
    start = time.time()
    print("4. Querying PromoBanner...")
    promo_sections = list(PromoBanner.objects.filter(is_active=True).prefetch_related('items').order_by('homepage_order'))
    print(f"   Done: {len(promo_sections)} promo sections in {time.time() - start:.2f}s")
    
    start = time.time()
    print("5. Querying Category (top-level)...")
    categories = list(Category.objects.filter(parent__isnull=True, is_active=True).order_by('homepage_order', 'name')[:12])
    print(f"   Done: {len(categories)} categories in {time.time() - start:.2f}s")
    
    start = time.time()
    print("6. Preparing shop_by_categories...")
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
    print(f"   Done in {time.time() - start:.2f}s")
    
    start = time.time()
    print("7. Querying AboutUs...")
    about_us = AboutUs.objects.filter(is_active=True).first()
    print(f"   Done in {time.time() - start:.2f}s")
    
    start = time.time()
    print("8. Querying MissionVision...")
    mv_sections = list(MissionVision.objects.filter(section_type__in=['mission', 'vision'], is_active=True))
    mission = next((mv for mv in mv_sections if mv.section_type == 'mission'), None)
    vision = next((mv for mv in mv_sections if mv.section_type == 'vision'), None)
    print(f"   Done in {time.time() - start:.2f}s")
    
    start = time.time()
    print("9. Querying Service, Counter, WhyUsCard, Partner, GalleryItem...")
    services = list(Service.objects.filter(is_active=True).order_by('order'))
    counters = list(Counter.objects.filter(is_active=True).order_by('order'))
    why_us = list(WhyUsCard.objects.filter(is_active=True).order_by('order'))
    partners = list(Partner.objects.filter(is_active=True).order_by('order'))
    gallery = list(GalleryItem.objects.filter(is_active=True).order_by('order')[:8])
    print(f"   Done: services={len(services)}, counters={len(counters)}, why_us={len(why_us)}, partners={len(partners)}, gallery={len(gallery)} in {time.time() - start:.2f}s")
    
    start = time.time()
    print("10. Querying Testimonial, Client, SocialPost...")
    testimonials = list(Testimonial.objects.filter(is_active=True).order_by('order'))
    public_clients = list(Client.objects.filter(category='Public', is_active=True).order_by('order'))
    private_clients = list(Client.objects.filter(category='Private', is_active=True).order_by('order'))
    social_posts = list(SocialPost.objects.all().order_by('order')[:6])
    print(f"    Done: testimonials={len(testimonials)}, public={len(public_clients)}, private={len(private_clients)}, social={len(social_posts)} in {time.time() - start:.2f}s")
    
    start = time.time()
    print("11. Querying Product (latest_products)...")
    latest_products = list(Product.objects.filter(quantity__gt=0, is_active=True).select_related('category', 'brand').prefetch_related('offers', 'images').order_by('-id')[:8])
    print(f"    Done: {len(latest_products)} in {time.time() - start:.2f}s")
    
    start = time.time()
    print("12. Querying Product (active_offers)...")
    now = timezone.now()
    active_offers_products = list(Product.objects.filter(is_active=True, quantity__gt=0).filter(
        models.Q(offers__start_date__lte=now, offers__end_date__gte=now) |
        models.Q(sale_price__isnull=False, sale_price__lt=models.F('regular_price'))
    ).distinct().select_related('category', 'brand').prefetch_related('offers', 'images'))
    print(f"    Done: {len(active_offers_products)} in {time.time() - start:.2f}s")
    
    start = time.time()
    print("13. Querying Product (featured_products)...")
    featured_products = list(Product.objects.filter(exclusive_products=True, is_active=True, quantity__gt=0).select_related('category', 'brand').prefetch_related('offers', 'images').order_by('-id'))
    print(f"    Done: {len(featured_products)} in {time.time() - start:.2f}s")
    
    start = time.time()
    print("14. Querying and attaching offers info...")
    all_active_offers = list(Offer.objects.filter(start_date__lte=now, end_date__gte=now).prefetch_related('products', 'categories', 'brands'))
    def attach_price_info(product_list):
        for p in product_list:
            p.price_info = p.get_best_price_info(prefetched_offers=all_active_offers)
    attach_price_info(latest_products)
    attach_price_info(featured_products)
    attach_price_info(active_offers_products)
    print(f"    Done in {time.time() - start:.2f}s")
    
    start = time.time()
    print("15. Querying Collection...")
    collections = list(Collection.objects.filter(is_active=True).prefetch_related(
        'products', 
        'products__category',
        'products__brand',
        'products__offers',
        'products__images'
    ))
    for col in collections:
        attach_price_info(col.products.all())
    print(f"    Done: {len(collections)} collections in {time.time() - start:.2f}s")
    
    start = time.time()
    print("16. Querying Brand...")
    brands = list(Brand.objects.filter(show_on_homepage=True, is_active=True).order_by('order'))
    print(f"    Done: {len(brands)} brands in {time.time() - start:.2f}s")
    
    start = time.time()
    print("17. Rendering Template...")
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
    
    factory = RequestFactory()
    request = factory.get('/')
    request.session = DummySession()
    request._messages = FallbackStorage(request)
    
    from django.shortcuts import render
    response = render(request, 'index.html', context)
    print(f"    Done rendering index.html! Status code: {response.status_code} in {time.time() - start:.2f}s")
    
    # Save a copy of the rendered HTML to verify
    with open('scratch/rendered_homepage.html', 'wb') as f:
        f.write(response.content)
    print("Saved rendered HTML to scratch/rendered_homepage.html")

if __name__ == "__main__":
    try:
        run_diagnostic()
    except Exception as e:
        print("\n--- Error rendering homepage ---")
        import traceback
        traceback.print_exc()
