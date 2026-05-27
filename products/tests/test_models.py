import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from products.models import Category, Brand, Product, Offer


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, category, brand):
        product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            category=category,
            brand=brand,
            regular_price='99.99',
            sale_price='79.99',
            quantity=10,
            is_active=True,
        )
        assert product.name == 'Test Product'
        assert product.quantity == 10
        assert product.is_active is True
        assert product.sku_id is not None

    def test_product_sku_generation(self, category, brand):
        product1 = Product.objects.create(
            name='Test Product 1',
            slug='test-product-1',
            category=category,
            brand=brand,
            regular_price='99.99',
            sale_price='79.99',
            quantity=10,
            is_active=True,
        )
        product2 = Product.objects.create(
            name='Test Product 2',
            slug='test-product-2',
            category=category,
            brand=brand,
            regular_price='89.99',
            sale_price='69.99',
            quantity=5,
            is_active=True,
        )

        assert product1.sku_id is not None
        assert product2.sku_id is not None
        assert product1.sku_id != product2.sku_id

    def test_product_image_url_fallback(self, category, brand):
        product = Product.objects.create(
            name='Test Product',
            slug='test-product-img',
            category=category,
            brand=brand,
            is_active=True,
        )
        assert 'placeholder' in product.get_image_url

    def test_product_slug_auto_generation(self, category, brand):
        product = Product.objects.create(
            name='Test Product Auto Slug',
            category=category,
            brand=brand,
            is_active=True,
        )
        assert product.slug == 'test-product-auto-slug'

    def test_product_features_list(self, category, brand):
        product = Product.objects.create(
            name='Test Product Features',
            slug='test-product-features',
            category=category,
            brand=brand,
            features='Feature 1\nFeature 2\nFeature 3',
            is_active=True,
        )
        features = product.features_list
        assert len(features) == 3
        assert 'Feature 1' in features
        assert 'Feature 2' in features
        assert 'Feature 3' in features

    def test_product_features_list_empty(self, category, brand):
        product = Product.objects.create(
            name='Test Product No Features',
            slug='test-product-no-features',
            category=category,
            brand=brand,
            is_active=True,
        )
        features = product.features_list
        assert features == []

    def test_product_is_in_stock(self, category, brand):
        product = Product.objects.create(
            name='Test Product Stock',
            slug='test-product-stock',
            category=category,
            brand=brand,
            quantity=10,
            shipping_status='available',
            is_active=True,
        )
        assert product.is_in_stock() is True

        product.quantity = 0
        product.save()
        assert product.is_in_stock() is False

        product.quantity = 10
        product.shipping_status = 'out_of_stock'
        product.save()
        assert product.is_in_stock() is False


@pytest.mark.django_db
class TestCategoryModel:
    def test_category_creation(self):
        category = Category.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True,
        )
        assert category.name == 'Test Category'
        assert category.is_active is True

    def test_category_descendant_ids(self, category):
        child = Category.objects.create(
            name='Child Category',
            slug='child-category',
            parent=category,
            is_active=True,
        )

        descendant_ids = category.get_descendant_ids(include_self=True)
        assert category.id in descendant_ids
        assert child.id in descendant_ids
        assert len(descendant_ids) == 2

    def test_category_ancestors(self, category, subcategory):
        ancestors = subcategory.get_ancestors()
        assert len(ancestors) >= 1
        assert category in ancestors


@pytest.mark.django_db
class TestBrandModel:
    def test_brand_creation(self):
        brand = Brand.objects.create(
            name='Test Brand',
            slug='test-brand',
            is_active=True,
        )
        assert brand.name == 'Test Brand'
        assert brand.is_active is True

    def test_brand_image_url_fallback(self):
        brand = Brand.objects.create(
            name='Test Brand No Logo',
            slug='test-brand-no-logo',
            is_active=True,
        )
        assert 'placeholder' in brand.get_image_url


@pytest.mark.django_db
class TestOfferModel:
    def test_offer_creation(self, active_offer):
        assert active_offer.name == 'Test Offer'
        assert active_offer.offer_type == 'percentage'
        assert active_offer.discount_value == Decimal('25')

    def test_offer_str_representation(self, active_offer):
        assert str(active_offer) == 'Test Offer'


@pytest.mark.django_db
class TestProductPriceCalculation:
    def test_regular_price_without_offer(self, product):
        price_info = product.get_best_price_info()
        assert price_info['final_price'] == Decimal('79.99')
        assert price_info['regular_price'] == Decimal('99.99')

    def test_price_calculation_with_percentage_offer(self, product, active_offer):
        price_info = product.get_best_price_info()
        assert price_info['has_offer'] is True
        assert price_info['final_price'] < Decimal('79.99')
        assert price_info['offer'] is not None

    def test_price_info_with_prefetched_offers(self, product, active_offer):
        now = timezone.now()
        active_offers = list(Offer.objects.filter(
            start_date__lte=now,
            end_date__gte=now
        ).prefetch_related('products', 'categories', 'brands'))

        price_info = product.get_best_price_info(prefetched_offers=active_offers)
        assert price_info['has_offer'] is True

    def test_price_calculation_no_sale_price(self, category, brand):
        product = Product.objects.create(
            name='Regular Price Only',
            slug='regular-price-only',
            category=category,
            brand=brand,
            regular_price='100.00',
            quantity=10,
            is_active=True,
        )
        price_info = product.get_best_price_info()
        assert price_info['final_price'] == Decimal('100.00')
        assert price_info['regular_price'] == Decimal('100.00')
        assert price_info['has_offer'] is False