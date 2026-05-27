from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from jkr.views_21st import (
    home_21st, product_list_21st, product_detail_21st,
    cart_21st, checkout_21st,
    admin_dashboard_21st, admin_products_21st, admin_orders_21st,
    admin_customers_21st, admin_inventory_21st,
    admin_newsletter_21st, admin_social_21st, admin_testimonials_21st,
    admin_locations_21st, admin_announcements_21st
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
    path('', include('core.urls')),   # root → core.views.home
    
    # 21st Century Premium Frontend
    path('21st/', home_21st, name='home_21st'),
    path('21st/products/', product_list_21st, name='product_list_21st'),
    path('21st/product/<slug:slug>/', product_detail_21st, name='product_detail_21st'),
    path('21st/cart/', cart_21st, name='cart_21st'),
    path('21st/checkout/', checkout_21st, name='checkout_21st'),
    
    # 21st Century Admin Dashboard
    path('21st/admin/', admin_dashboard_21st, name='admin_dashboard_21st'),
    path('21st/admin/products/', admin_products_21st, name='admin_products_21st'),
    path('21st/admin/orders/', admin_orders_21st, name='admin_orders_21st'),
    path('21st/admin/customers/', admin_customers_21st, name='admin_customers_21st'),
    path('21st/admin/inventory/', admin_inventory_21st, name='admin_inventory_21st'),
    path('21st/admin/newsletter/', admin_newsletter_21st, name='admin_newsletter_21st'),
    path('21st/admin/social/', admin_social_21st, name='admin_social_21st'),
    path('21st/admin/testimonials/', admin_testimonials_21st, name='admin_testimonials_21st'),
    path('21st/admin/locations/', admin_locations_21st, name='admin_locations_21st'),
    path('21st/admin/announcements/', admin_announcements_21st, name='admin_announcements_21st'),
    
    # 21st Century Admin Action APIs (AJAX)
    path('21st/admin/api/products/<int:pk>/delete/', admin_products_21st, name='admin_product_delete_api'), # We can route them or define custom views
    path('21st/admin/api/products/<int:pk>/toggle/', admin_products_21st, name='admin_product_toggle_api'),
    path('21st/admin/api/orders/<int:pk>/status/', admin_orders_21st, name='admin_order_status_api'),
    path('21st/admin/api/inventory/<int:pk>/adjust/', admin_inventory_21st, name='admin_inventory_adjust_api'),
    path('21st/admin/api/newsletter/<int:pk>/delete/', admin_newsletter_21st, name='admin_newsletter_delete_api'),
    path('21st/admin/api/testimonials/action/', admin_testimonials_21st, name='admin_testimonials_action_api'),
    path('21st/admin/api/locations/action/', admin_locations_21st, name='admin_locations_action_api'),
    path('21st/admin/api/announcements/action/', admin_announcements_21st, name='admin_announcements_action_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

