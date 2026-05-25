from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0015_alter_pagehero_page'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(
                    blank=True,
                    max_length=255,
                    help_text="Optional overlay caption (e.g. 'Blush Cascade'). Shown in the floating tag."
                )),
                ('image', models.ImageField(
                    blank=True,
                    null=True,
                    upload_to='hero_slides/',
                    help_text='Recommended: 900x1100px (portrait). JPG or WEBP. Max 2MB.'
                )),
                ('image_url', models.URLField(
                    blank=True,
                    null=True,
                    help_text='External image URL alternative.'
                )),
                ('alt_text', models.CharField(
                    blank=True,
                    default='Bloom & Petal \u2013 Hero Image',
                    max_length=255,
                    help_text='SEO alt text for the image.'
                )),
                ('order', models.PositiveIntegerField(
                    default=0,
                    help_text='Lower numbers appear first.'
                )),
                ('is_active', models.BooleanField(
                    choices=[(True, 'Active'), (False, 'Hidden')],
                    default=True,
                    verbose_name='Status'
                )),
            ],
            options={
                'verbose_name': 'Hero Slide',
                'verbose_name_plural': 'Hero Slides',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HomepageSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # ── Announcement ──
                ('announcement_text', models.CharField(
                    default='\U0001f338 \xa0 Free delivery on orders over 200 AED \xa0|\xa0 Same-day delivery available \xa0\U0001f338',
                    help_text='Text shown in the top announcement bar.',
                    max_length=400
                )),
                ('show_announcement_bar', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Announcement Bar'
                )),
                # ── Hero text ──
                ('hero_eyebrow', models.CharField(
                    default="Dubai's Premier Florist",
                    help_text='Small uppercase label above the hero title.',
                    max_length=120
                )),
                ('hero_title_line1', models.CharField(
                    default='Flowers that',
                    help_text='First line of the large hero title.',
                    max_length=120
                )),
                ('hero_title_em', models.CharField(
                    default='speak',
                    help_text='Italic/rose-coloured word in the middle of the hero title.',
                    max_length=80
                )),
                ('hero_title_line2', models.CharField(
                    default='your heart',
                    help_text='Third line of the large hero title.',
                    max_length=120
                )),
                ('hero_subtitle', models.TextField(
                    default='Handcrafted arrangements for every occasion \u2014 from intimate gestures to grand celebrations. Delivered fresh across Dubai.',
                    help_text='Paragraph below the hero title.'
                )),
                # ── Hero CTAs ──
                ('hero_btn1_text', models.CharField(default='Shop Collection', max_length=80)),
                ('hero_btn1_link', models.CharField(
                    default='/products/',
                    help_text='URL or path for the primary hero button.',
                    max_length=255
                )),
                ('hero_btn2_text', models.CharField(default='Explore Occasions', max_length=80)),
                ('hero_btn2_link', models.CharField(
                    default='/products/',
                    help_text='URL or path for the secondary hero button.',
                    max_length=255
                )),
                # ── Hero Floating Tag ──
                ('hero_tag_label', models.CharField(
                    default="Today's Pick",
                    help_text='Small label in the floating card on the hero image panel.',
                    max_length=80
                )),
                ('hero_tag_value', models.CharField(
                    default='Blush Cascade',
                    help_text='Main text in the floating card on the hero image panel.',
                    max_length=120
                )),
                ('show_hero_tag', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Show Hero Tag'
                )),
                # ── Section Labels ──
                ('featured_eyebrow', models.CharField(default='Curated Selection', max_length=100)),
                ('featured_title', models.CharField(default='Latest Arrivals', max_length=200)),
                ('featured_subtitle', models.TextField(
                    blank=True,
                    default='Each arrangement is crafted by our expert florists using only the freshest blooms'
                )),
                ('bestsellers_eyebrow', models.CharField(default='Most Loved', max_length=100)),
                ('bestsellers_title', models.CharField(default='Best Sellers', max_length=200)),
                ('testimonials_eyebrow', models.CharField(default='Happy Customers', max_length=100)),
                ('testimonials_title', models.CharField(default='What they say', max_length=200)),
                # ── Section Visibility ──
                ('show_category_pills', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Category Pills Strip'
                )),
                ('show_featured_products', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Latest Arrivals Section'
                )),
                ('show_why_strip', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Why Us Strip'
                )),
                ('show_best_sellers', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Best Sellers Section'
                )),
                ('show_testimonials', models.BooleanField(
                    choices=[(True, 'Show'), (False, 'Hide')],
                    default=True,
                    verbose_name='Testimonials Section'
                )),
            ],
            options={
                'verbose_name': 'Homepage Settings',
                'verbose_name_plural': 'Homepage Settings',
            },
        ),
    ]
