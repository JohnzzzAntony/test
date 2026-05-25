# Generated manually for Flower District Theme Redesign
# This migration adds the comprehensive set of new design tokens and color fields
# required for the www.flowerdistrict.ae visual identity (deep blue + clean white).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_add_font_accent_and_updated_at'),
    ]

    operations = [
        # === New Core Color Palette Fields (Flower District Deep Blue Theme) ===
        migrations.AddField(
            model_name='designsettings',
            name='accent_color',
            field=models.CharField(default='#0081ff', help_text='Bright Blue accent for CTAs and highlights.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='accent_hover_color',
            field=models.CharField(default='#0066cc', help_text='Accent color for hover states.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='text_accent_color',
            field=models.CharField(default='#114084', help_text='Accent text color.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='border_hover_color',
            field=models.CharField(default='#cccccc', help_text='Border color on hover.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='header_border_color',
            field=models.CharField(default='#e5e5e5', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='footer_heading_color',
            field=models.CharField(default='#FFFFFF', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='category_bg_color',
            field=models.CharField(default='#f8f9fa', help_text='Category section background.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='price_color',
            field=models.CharField(default='#1a1a1a', help_text='Product price text color.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='sale_price_color',
            field=models.CharField(default='#c0392b', help_text='Sale price color.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='rating_star_color',
            field=models.CharField(default='#f59e0b', help_text='Rating star color.', max_length=50),
        ),

        # === Button Color System ===
        migrations.AddField(
            model_name='designsettings',
            name='button_primary_bg',
            field=models.CharField(default='#114084', help_text='Primary button background.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_primary_text',
            field=models.CharField(default='#FFFFFF', help_text='Primary button text.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_primary_hover_bg',
            field=models.CharField(default='#0d3a6e', help_text='Primary button hover background.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_secondary_bg',
            field=models.CharField(default='#FFFFFF', help_text='Secondary button background.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_secondary_text',
            field=models.CharField(default='#114084', help_text='Secondary button text.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_secondary_border',
            field=models.CharField(default='#114084', help_text='Secondary button border.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_secondary_hover_bg',
            field=models.CharField(default='#114084', help_text='Secondary button hover background.', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='button_secondary_hover_text',
            field=models.CharField(default='#FFFFFF', help_text='Secondary button hover text.', max_length=50),
        ),

        # === Additional Shape & Behavior Fields ===
        migrations.AddField(
            model_name='designsettings',
            name='input_radius',
            field=models.CharField(default='4px', help_text='Form input border radius', max_length=50),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='enable_shadows',
            field=models.BooleanField(choices=[(True, 'Enabled'), (False, 'Disabled')], default=True, verbose_name='Card Shadows'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='enable_hover_effects',
            field=models.BooleanField(choices=[(True, 'Enabled'), (False, 'Disabled')], default=True, verbose_name='Hover Effects'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='animation_duration',
            field=models.PositiveIntegerField(default=400, help_text='Animation duration in ms'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='spacing_unit',
            field=models.PositiveIntegerField(default=8, help_text='Base spacing unit in px (e.g. 8 for 8px scale)'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='section_padding',
            field=models.PositiveIntegerField(default=64, help_text='Section padding in px'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='container_padding',
            field=models.PositiveIntegerField(default=48, help_text='Container padding in px'),
        ),

        # === Homepage Best Sellers + Trust Badges ===
        migrations.AddField(
            model_name='designsettings',
            name='hp_bestsellers_title',
            field=models.CharField(default='Our Best <span class="accent">Sellers</span>', max_length=255),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='show_hp_bestsellers',
            field=models.BooleanField(choices=[(True, 'Show'), (False, 'Hide')], default=True, verbose_name='Home Best Sellers'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='show_trust_badges',
            field=models.BooleanField(choices=[(True, 'Show'), (False, 'Hide')], default=True, verbose_name='Trust Badges'),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_1_title',
            field=models.CharField(default='Fast Delivery', max_length=100),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_1_text',
            field=models.CharField(default='Safe & fast deliveries all over UAE', max_length=200),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_2_title',
            field=models.CharField(default='Secure Payment', max_length=100),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_2_text',
            field=models.CharField(default='VISA, Mastercard and Cash on Delivery', max_length=200),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_3_title',
            field=models.CharField(default='Customer Support', max_length=100),
        ),
        migrations.AddField(
            model_name='designsettings',
            name='trust_badge_3_text',
            field=models.CharField(default='We are here 24/7 for your queries', max_length=200),
        ),

        # === Counter animation default change (runner → fade) ===
        # We just alter the default; no data change needed.
        migrations.AlterField(
            model_name='designsettings',
            name='counter_animation_style',
            field=models.CharField(default='fade', max_length=50),
        ),

        # Note: Old removed fields (enable_glassmorphism, enable_neumorphism, enable_ambient_glow, font_secondary, theme_variant, etc.)
        # are intentionally left for a future cleanup migration to avoid data loss in production.
        # The new frontend only reads the fields defined above.
    ]
