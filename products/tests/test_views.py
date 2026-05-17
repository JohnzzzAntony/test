import pytest
from django.test import Client


@pytest.mark.django_db
class TestProductListView:
    def test_product_list_loads(self):
        client = Client()
        response = client.get('/products/')
        assert response.status_code == 200

    def test_product_list_with_query(self):
        client = Client()
        response = client.get('/products/?q=test')
        assert response.status_code == 200

    def test_product_list_with_price_filter(self):
        client = Client()
        response = client.get('/products/?min_price=10&max_price=100')
        assert response.status_code == 200

    def test_product_list_with_sort(self):
        client = Client()
        response = client.get('/products/?sort=price_low')
        assert response.status_code == 200


@pytest.mark.django_db
class TestCategoryView:
    def test_category_index_loads(self):
        client = Client()
        response = client.get('/products/categories/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestProductDetailView:
    def test_product_detail_loads(self, product):
        client = Client()
        response = client.get(f'/products/{product.slug}/')
        assert response.status_code == 200

    def test_product_detail_by_id_loads(self, product):
        client = Client()
        response = client.get(f'/products/{product.id}/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestBrandViews:
    def test_brand_list_loads(self):
        client = Client()
        response = client.get('/products/brands/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestWishlistViews:
    def test_wishlist_requires_login(self, client):
        response = client.get('/products/wishlist/')
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_toggle_wishlist_requires_login(self, client, product):
        response = client.post(f'/products/wishlist/toggle/{product.id}/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestSubcategoriesAPI:
    def test_get_subcategories_requires_admin(self, client, category):
        response = client.get(f'/products/subcategories/{category.id}/')
        assert response.status_code == 302

    def test_get_subcategories_admin(self, client, category, django_user_model):
        admin = django_user_model.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        client.force_login(admin)
        response = client.get(f'/products/ajax/subcategories/{category.id}/')
        assert response.status_code == 200