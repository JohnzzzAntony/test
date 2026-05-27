from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories/api', views.CategoryViewSet, basename='category_api')

app_name = 'products'

urlpatterns = [
    path('api/', include(router.urls)), # API Endpoints
    path('', views.category_index, name='category_index'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('results/', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('category/<path:hierarchy_path>/', views.category_detail, name='category_hierarchy_detail'),
    
    path('brands/', views.brand_list, name='brand_list'),
    path('brand/<slug:slug>/', views.brand_detail, name='brand_detail'),
    path('collections/', views.collection_list, name='collection_list'),

    
    # Internal Admin APIs
    path('api/media/delete/<int:pk>/', views.delete_product_media, name='delete_product_media'),
    path('api/product/clear-image/<int:pk>/', views.clear_primary_product_image, name='clear_primary_product_image'),
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('api/subcategories/<int:parent_id>/', views.get_subcategories, name='get_subcategories'),
    
    path('collection/<slug:slug>/', views.collection_detail, name='collection_detail'),
    re_path(r'^id/(?P<pk>.*)/$', views.product_detail, name='product_detail'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
