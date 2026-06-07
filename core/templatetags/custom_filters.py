from django import template
from core.models import SiteSettings
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.simple_tag
def get_site_settings():
    return SiteSettings.objects.first()

@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(Decimal(str(value)) * Decimal(str(arg)))
    except (ValueError, TypeError, InvalidOperation):
        return 0

@register.filter(name='split')
def split(value, key):
    return value.split(key)

@register.filter(name='get_attr')
def get_attr(obj, attr):
    return getattr(obj, attr, None)

@register.filter(name='render_stars')
def render_stars(rating):
    from django.utils.safestring import mark_safe
    try:
        rating = float(rating)
    except (ValueError, TypeError):
        rating = 0.0
    
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    
    html = ''
    for _ in range(full_stars):
        html += '<i class="fas fa-star"></i>'
    if half_star:
        html += '<i class="fas fa-star-half-alt"></i>'
    for _ in range(empty_stars):
        html += '<i class="far fa-star"></i>'
        
    return mark_safe(html)
