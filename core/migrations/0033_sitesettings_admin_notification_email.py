from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_client_image_alt_sitesettings_facebook_pixel_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='admin_notification_email',
            field=models.EmailField(
                blank=True,
                help_text='Email address to receive admin notifications (new orders, contact form submissions, etc.)',
                verbose_name='Admin Notification Email',
            ),
        ),
    ]
