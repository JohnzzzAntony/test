import stripe
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from .models import SubscriptionPlan, UserSubscription
from datetime import datetime

User = get_user_model()

class SubscriptionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.login(username='testuser', password='password')
        
        self.plan = SubscriptionPlan.objects.create(
            name='Pro Plan',
            description='Test Pro Plan',
            price=29.00,
            currency='USD',
            interval='month',
            stripe_price_id='price_123',
            is_active=True
        )

    def test_pricing_view_non_staff(self):
        response = self.client.get(reverse('subscriptions:pricing'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/profile/?tab=billing')

    def test_pricing_view_staff(self):
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('subscriptions:pricing'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('subscriptions:admin_plans'))

    @patch('stripe.checkout.Session.create')
    def test_create_checkout_session(self, mock_checkout_create):
        # Mock session URL
        mock_session = MagicMock()
        mock_session.url = 'https://checkout.stripe.com/test'
        mock_checkout_create.return_value = mock_session

        response = self.client.get(reverse('subscriptions:create_checkout', args=[self.plan.id]))
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://checkout.stripe.com/test')
        mock_checkout_create.assert_called_once()

    def test_create_checkout_session_not_found(self):
        response = self.client.get(reverse('subscriptions:create_checkout', args=[999]))
        self.assertEqual(response.status_code, 404)

    @patch('stripe.billing_portal.Session.create')
    def test_create_portal_session_active(self, mock_portal_create):
        # Create a UserSubscription with a stripe_customer_id
        UserSubscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_123',
            status='active'
        )

        mock_session = MagicMock()
        mock_session.url = 'https://billing.stripe.com/test'
        mock_portal_create.return_value = mock_session

        response = self.client.get(reverse('subscriptions:create_portal_session'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'https://billing.stripe.com/test')
        mock_portal_create.assert_called_once()

    def test_create_portal_session_no_customer(self):
        # No customer ID set
        response = self.client.get(reverse('subscriptions:create_portal_session'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/profile/?tab=billing')

    def test_checkout_success_and_cancel_views(self):
        response = self.client.get(reverse('subscriptions:success'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('subscriptions:cancel'))
        self.assertEqual(response.status_code, 200)

    @patch('stripe.Webhook.construct_event')
    @patch('stripe.Subscription.retrieve')
    def test_webhook_checkout_session_completed(self, mock_sub_retrieve, mock_construct_event):
        # Setup mock event
        mock_construct_event.return_value = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'metadata': {
                        'user_id': self.user.id,
                        'plan_id': self.plan.id,
                    },
                    'customer': 'cus_123',
                    'subscription': 'sub_123'
                }
            }
        }

        # Setup mock subscription retrieve
        mock_stripe_sub = MagicMock()
        mock_stripe_sub.status = 'active'
        mock_stripe_sub.current_period_start = 1600000000
        mock_stripe_sub.current_period_end = 1600086400
        mock_sub_retrieve.return_value = mock_stripe_sub

        with self.settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=123,v1=123'
            )
        
        self.assertEqual(response.status_code, 200)
        
        # Check UserSubscription was created/updated
        user_sub = UserSubscription.objects.get(user=self.user)
        self.assertEqual(user_sub.stripe_customer_id, 'cus_123')
        self.assertEqual(user_sub.stripe_subscription_id, 'sub_123')
        self.assertEqual(user_sub.plan, self.plan)
        self.assertEqual(user_sub.status, 'active')

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_updated(self, mock_construct_event):
        user_sub = UserSubscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_123',
            stripe_subscription_id='sub_123',
            plan=self.plan,
            status='active'
        )

        mock_construct_event.return_value = {
            'type': 'customer.subscription.updated',
            'data': {
                'object': {
                    'id': 'sub_123',
                    'status': 'past_due',
                    'current_period_start': 1600000000,
                    'current_period_end': 1600086400,
                    'cancel_at_period_end': True
                }
            }
        }

        with self.settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=123,v1=123'
            )
        
        self.assertEqual(response.status_code, 200)
        user_sub.refresh_from_db()
        self.assertEqual(user_sub.status, 'past_due')
        self.assertTrue(user_sub.cancel_at_period_end)

    @patch('stripe.Webhook.construct_event')
    def test_webhook_subscription_deleted(self, mock_construct_event):
        user_sub = UserSubscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_123',
            stripe_subscription_id='sub_123',
            plan=self.plan,
            status='active'
        )

        mock_construct_event.return_value = {
            'type': 'customer.subscription.deleted',
            'data': {
                'object': {
                    'id': 'sub_123',
                }
            }
        }

        with self.settings(STRIPE_WEBHOOK_SECRET='whsec_test'):
            response = self.client.post(
                reverse('subscriptions:webhook'),
                data='{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='t=123,v1=123'
            )
        
        self.assertEqual(response.status_code, 200)
        user_sub.refresh_from_db()
        self.assertEqual(user_sub.status, 'expired')
