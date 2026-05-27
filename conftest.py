import pytest
from django.conf import settings


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def category(db):
    from products.models import Category
    cat = Category.objects.create(
        name='Test Category',
        slug='test-category',
        is_active=True,
    )
    return cat


@pytest.fixture
def brand(db):
    from products.models import Brand
    b = Brand.objects.create(
        name='Test Brand',
        slug='test-brand',
        is_active=True,
    )
    return b


@pytest.fixture
def product(db, category, brand):
    from products.models import Product
    p = Product.objects.create(
        name='Test Product',
        slug='test-product',
        category=category,
        brand=brand,
        regular_price='99.99',
        sale_price='79.99',
        quantity=10,
        is_active=True,
    )
    return p


@pytest.fixture
def subcategory(db, category):
    from products.models import Category
    sub = Category.objects.create(
        name='Sub Category',
        slug='sub-category',
        parent=category,
        is_active=True,
    )
    return sub


@pytest.fixture
def active_offer(db, category, brand, product):
    from products.models import Offer
    from datetime import timedelta
    from django.utils import timezone
    from decimal import Decimal
    now = timezone.now()
    offer = Offer.objects.create(
        name='Test Offer',
        offer_type='percentage',
        discount_value=Decimal('25'),
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=30),
    )
    offer.categories.add(category)
    offer.brands.add(brand)
    offer.products.add(product)
    return offer