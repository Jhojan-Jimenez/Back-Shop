# Generated by Django 4.2.16 on 2024-10-23 00:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shipping', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shipping',
            options={'ordering': ['price'], 'verbose_name': 'Shipping', 'verbose_name_plural': 'Shipping'},
        ),
    ]