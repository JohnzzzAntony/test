# Generated migration: 0021_reset_homepagesettings_content
# Purpose: Clear stale florist-theme content from HomepageSettings and
# replace it with content that accurately reflects the live medical
# equipment homepage (index.html / JKR International).

from django.db import migrations


def reset_homepage_settings(apps, schema_editor):
    """
    Reset the singleton HomepageSettings record with content that matches
    the actual live homepage for JKR International (medical equipment).

    Context:
    - The hero banner is driven by sliders_heroslider, NOT HomepageSettings hero fields.
    - DesignSettings (core) controls global section titles / theme colours.
    - HomepageSettings controls: section toggles, section-level eyebrow/title
      labels for Latest Products, Best Sellers, Testimonials, and product pins.
    """
    HomepageSettings = apps.get_model('pages', 'HomepageSettings')

    # Delete the stale florist record and create a clean one with correct defaults.
    HomepageSettings.objects.all().delete()

    HomepageSettings.objects.create(
        # ── Announcement Bar ─────────────────────────────────
        show_announcement_bar=True,
        announcement_text=(
            '\U0001f4e6\u00a0 Free delivery on qualifying orders'
            ' \u00a0|\u00a0 Same-day dispatch available'
            ' \u00a0|\u00a0 ISO & FDA certified products \u00a0\U0001f3e5'
        ),

        # ── Section Visibility ────────────────────────────────
        show_category_pills=True,
        show_featured_products=True,
        show_why_strip=True,
        show_best_sellers=True,
        show_testimonials=True,

        # ── Latest Products section (Section 4) ──────────────
        featured_eyebrow='New Arrivals',
        featured_title='Latest Products',
        featured_subtitle='Discover our newest medical equipment and healthcare supplies.',

        # ── Best Sellers / On Sale section (Section 6) ────────
        bestsellers_eyebrow='Top Picks',
        bestsellers_title='Our Best Sellers',

        # ── Testimonials section (Section 8) ─────────────────
        testimonials_eyebrow='Client Reviews',
        testimonials_title='What Our Customers Say',

        # ── Hero Text fields (NOT rendered in current homepage) ─
        # Stored for potential future use only.
        hero_eyebrow='Trusted by 500+ Healthcare Providers',
        hero_title_line1='Equipping Healthcare',
        hero_title_em='Modern Era',
        hero_title_line2='for the',
        hero_subtitle=(
            'Cutting-edge medical equipment and supplies, curated for hospitals, '
            'clinics, and practices worldwide. Precision, reliability, and care '
            'in every product.'
        ),
        hero_btn1_text='Browse Catalog',
        hero_btn1_link='/products/',
        hero_btn2_text='Request Quote',
        hero_btn2_link='/contact/',

        # ── Hero Floating Tag (NOT rendered in current homepage) ─
        show_hero_tag=False,
        hero_tag_label='New Arrival',
        hero_tag_value='Latest Medical Equipment',
    )


def reverse_reset(apps, schema_editor):
    """Reverse: restore the florist record (best effort — cannot recover M2M)."""
    HomepageSettings = apps.get_model('pages', 'HomepageSettings')
    HomepageSettings.objects.all().delete()
    HomepageSettings.objects.create(
        show_announcement_bar=True,
        announcement_text='\U0001f338\u00a0 Free delivery on orders over 200 AED \u00a0|\u00a0 Same-day delivery available \u00a0\U0001f338',
        featured_eyebrow='Curated Selection',
        featured_title='Latest Arrivals',
        featured_subtitle='Each arrangement is crafted by our expert florists using only the freshest blooms',
        bestsellers_eyebrow='Most Loved',
        bestsellers_title='Best Sellers',
        testimonials_eyebrow='Happy Customers',
        testimonials_title='What they say',
        hero_eyebrow="Dubai's Premier Florist",
        hero_title_line1='Flowers that',
        hero_title_em='speak',
        hero_title_line2='your heart',
        hero_subtitle=(
            'Handcrafted arrangements for every occasion \u2014 from intimate gestures '
            'to grand celebrations. Delivered fresh across Dubai.'
        ),
        hero_btn1_text='Shop Collection',
        hero_btn1_link='/products/',
        hero_btn2_text='Explore Occasions',
        hero_btn2_link='/products/',
        show_hero_tag=True,
        hero_tag_label="Today's Pick",
        hero_tag_value='Blush Cascade',
    )


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0020_auto_20260607_0237'),
    ]

    operations = [
        migrations.RunPython(reset_homepage_settings, reverse_reset),
    ]
