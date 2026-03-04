# Generated manually to update PropertyImage model and add missing fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0004_alter_property_options_property_owner_and_more'),
    ]

    operations = [
        # Update PropertyImage fields to add help_text and constraints
        migrations.AlterField(
            model_name='propertyimage',
            name='image',
            field=models.ImageField(help_text='Image file (auto-synced to S3 if configured)', upload_to='property_images/%Y/%m/'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='alt_text',
            field=models.CharField(blank=True, help_text='Accessibility alt text for image', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='is_primary',
            field=models.BooleanField(default=False, help_text='Use as thumbnail/primary image in listings'),
        ),
        migrations.AlterField(
            model_name='propertyimage',
            name='order',
            field=models.PositiveIntegerField(default=0, help_text='Display order in gallery (0 = first)'),
        ),
        # Add indexes to PropertyImage
        migrations.AddIndex(
            model_name='propertyimage',
            index=models.Index(fields=['property', 'order'], name='properties_property_id_order_idx'),
        ),
    ]
