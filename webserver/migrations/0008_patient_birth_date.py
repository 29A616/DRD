# Generated by Django 5.1.4 on 2024-12-15 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0007_alter_diagnosticimage_gradcam_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='birth_date',
            field=models.DateField(default='1950-01-01'),
        ),
    ]