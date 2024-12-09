# Generated by Django 5.1.4 on 2024-12-09 20:57

import webserver.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0006_diagnosticimage_gradcam_image_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diagnosticimage',
            name='gradcam_image',
            field=models.ImageField(blank=True, null=True, upload_to=webserver.models.diagnostic_images_upload_to),
        ),
        migrations.AlterField(
            model_name='diagnosticimage',
            name='image',
            field=models.ImageField(upload_to=webserver.models.diagnostic_images_upload_to),
        ),
    ]
