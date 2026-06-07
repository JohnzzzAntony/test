import pytest
from django.urls import reverse
from django.test import Client
from pages.models import HomepageSettings

@pytest.mark.django_db
def test_homepage_settings_singleton():
    """Verify that HomepageSettings operates as a singleton."""
    settings_1 = HomepageSettings.get_settings()
    settings_2 = HomepageSettings.get_settings()
    
    assert settings_1 == settings_2
    assert HomepageSettings.objects.count() == 1

@pytest.mark.django_db
def test_homepage_settings_default_values():
    """Verify default values are properly populated on the singleton."""
    settings = HomepageSettings.get_settings()
    
    # Hero defaults
    assert settings.hero_badge_text == "Trusted by 500+ Healthcare Providers"
    assert "Equipping Healthcare" in settings.hero_title_html
    
    # Feature defaults
    assert settings.show_features_strip is True
    assert settings.feature_1_title == "Fast Shipping"
    
    # Categories defaults
    assert settings.categories_title == "Shop by Category"
    
    # Featured products defaults
    assert settings.featured_title == "Featured Products"
    
    # Testimonial defaults
    assert settings.testimonial_author_name == "Dr. James Davidson"
    
    # CTA defaults
    assert settings.cta_title == "Need Bulk Orders or Custom Quotes?"

@pytest.mark.django_db
def test_homepage_rendering_with_settings():
    """Verify settings control the visibility/content of homepage sections."""
    settings = HomepageSettings.get_settings()
    
    client = Client()
    response = client.get(reverse('core:home'))
    assert response.status_code == 200
    assert "Trusted by 500+ Healthcare Providers" in response.content.decode('utf-8')
    assert "Featured Products" in response.content.decode('utf-8')
    
    # Update settings to hide features and change titles
    settings.show_features_strip = False
    settings.featured_title = "Special Equipment Deals"
    settings.save()
    
    response = client.get(reverse('core:home'))
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Special Equipment Deals" in content
    # Verify the features section/text is not in content since features is hidden
    assert "Fast Shipping" not in content
