# Generated by Django 3.2.6 on 2021-09-23 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_auto_20210923_1800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='src',
            field=models.URLField(max_length=80000, unique=True),
        ),
    ]
