import pytest
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestAuthentication:
    def test_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123') is True

    def test_user_str_representation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        assert str(user) == 'testuser'

    def test_user_first_last_name(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.first_name == 'Test'
        assert user.last_name == 'User'
        assert user.get_full_name() == 'Test User'


@pytest.mark.django_db
class TestUserProfile:
    def test_user_profile_view_requires_login(self, client):
        response = client.get('/accounts/profile/')
        assert response.status_code == 302
        assert '/accounts/login/' in response.url

    def test_user_profile_view_authenticated(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        client.force_login(user)
        response = client.get('/accounts/profile/')
        assert response.status_code == 200

    def test_order_history_view_requires_login(self, client):
        response = client.get('/accounts/orders/')
        assert response.status_code == 302

    def test_order_history_view_authenticated(self, client, django_user_model):
        user = django_user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        client.force_login(user)
        response = client.get('/accounts/orders/')
        assert response.status_code == 200