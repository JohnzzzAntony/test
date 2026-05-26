import pytest
from django.test import Client
from django.utils import timezone


@pytest.mark.django_db
class TestHomepage:
    def test_homepage_loads(self):
        client = Client()
        response = client.get('/')
        assert response.status_code == 200

    def test_homepage_context(self):
        client = Client()
        response = client.get('/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_endpoint(self):
        client = Client()
        response = client.get('/health/')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'


@pytest.mark.django_db
class TestSiteSettings:
    def test_robots_txt_endpoint(self):
        from core.models import SiteSettings
        SiteSettings.objects.create(
            site_name='Test Site',
            robots_txt='User-agent: *\nDisallow: /admin/'
        )
        client = Client()
        response = client.get('/robots.txt')
        assert response.status_code == 200
        assert 'Disallow: /admin/' in response.content.decode()

    def test_robots_txt_default(self):
        client = Client()
        response = client.get('/robots.txt')
        assert response.status_code == 200


@pytest.mark.django_db
class TestAboutPage:
    def test_about_page_loads(self):
        client = Client()
        response = client.get('/about/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestServicesPage:
    def test_services_page_loads(self):
        client = Client()
        response = client.get('/services/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestGalleryPage:
    def test_gallery_page_loads(self):
        client = Client()
        response = client.get('/gallery/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestStoreLocations:
    def test_store_locations_page_loads(self):
        client = Client()
        response = client.get('/stores/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestNewsletter:
    def test_newsletter_subscribe_success(self):
        client = Client()
        response = client.post('/newsletter/subscribe/', {'email': 'test@example.com'})
        assert response.status_code == 302  # Redirects to home
        from core.models import NewsletterSubscription
        assert NewsletterSubscription.objects.filter(email='test@example.com').exists()

    def test_newsletter_subscribe_invalid_email(self):
        client = Client()
        response = client.post('/newsletter/subscribe/', {'email': 'invalid-email'})
        assert response.status_code == 302  # Redirects to home without saving
        from core.models import NewsletterSubscription
        assert not NewsletterSubscription.objects.filter(email='invalid-email').exists()