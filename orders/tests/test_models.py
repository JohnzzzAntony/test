import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from orders.models import CustomerOrder, CustomerOrderItem


@pytest.mark.django_db
class TestCustomerOrderModel:
    def test_order_creation(self):
        order = CustomerOrder.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+971501234567',
            country='UAE',
            city='Dubai',
            total_amount=Decimal('100.00'),
            payment_status='pending',
        )
        assert order.first_name == 'John'
        assert order.last_name == 'Doe'
        assert order.email == 'john@example.com'
        assert order.payment_status == 'pending'

    def test_order_str_representation(self):
        order = CustomerOrder.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+971501234567',
            country='UAE',
            city='Dubai',
            total_amount=Decimal('100.00'),
        )
        assert 'John' in str(order)
        assert 'Doe' in str(order)

    def test_order_full_name_property(self):
        order = CustomerOrder.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+971501234567',
            country='UAE',
            city='Dubai',
            total_amount=Decimal('100.00'),
        )
        assert order.full_name == 'John Doe'

    def test_order_status_history_on_creation(self):
        order = CustomerOrder.objects.create(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone='+971501234568',
            country='UAE',
            city='Dubai',
            total_amount=Decimal('200.00'),
            status='pending',
        )
        assert order.history.count() >= 1


@pytest.mark.django_db
class TestCustomerOrderItemModel:
    def test_order_item_creation(self, product):
        order = CustomerOrder.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+971501234567',
            country='UAE',
            city='Dubai',
            total_amount=Decimal('79.99'),
        )
        item = CustomerOrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            quantity=2,
            regular_price=Decimal('99.99'),
            offer_price=Decimal('79.99'),
            unit_price=Decimal('79.99'),
            total_price=Decimal('159.98'),
        )
        assert item.product_name == 'Test Product'
        assert item.quantity == 2
        assert item.total_price == Decimal('159.98')


@pytest.mark.django_db
class TestCartViews:
    def test_cart_view_loads(self, client):
        response = client.get(reverse('orders:enquiry_cart'))
        assert response.status_code == 200

    def test_add_to_cart_redirects(self, client, product):
        response = client.get(reverse('orders:add_to_cart', kwargs={'product_id': product.id}))
        assert response.status_code == 302

    def test_remove_from_cart_view(self, client, product):
        session = client.session
        session['enquiry_cart'] = {str(product.id): {'quantity': 2}}
        session.save()

        response = client.get(reverse('orders:remove_from_cart', kwargs={'product_id': product.id}))
        assert response.status_code == 302


@pytest.mark.django_db
class TestCheckoutFlow:
    def test_checkout_billing_requires_cart(self, client):
        session = client.session
        session['enquiry_cart'] = {}
        session.save()

        response = client.get(reverse('orders:checkout_billing'))
        assert response.status_code == 302

    def test_checkout_payment_requires_billing(self, client):
        session = client.session
        session['enquiry_cart'] = {}
        if 'checkout_billing' in session:
            del session['checkout_billing']
        session.save()

        response = client.get(reverse('orders:checkout_payment'))
        assert response.status_code == 302