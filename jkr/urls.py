from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from jkr.views_21st import (
    home_21st, product_list_21st, product_detail_21st,
    cart_21st, checkout_21st,
    admin_dashboard_21st, admin_products_21st, admin_orders_21st,
    admin_customers_21st, admin_inventory_21st
)

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('products/', include('products.urls')),
    path('blog/', include('blog.urls')),
    path('contact/', include('contact.urls')),
    path('enquiry-cart/', include('orders.urls')),
    path('accounts/', include('accounts.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('api/', include('jkr.api_urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
