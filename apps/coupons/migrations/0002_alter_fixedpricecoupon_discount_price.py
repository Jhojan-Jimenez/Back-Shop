# Generated by Django 4.2.16 on 2024-10-29 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coupons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixedpricecoupon',
            name='discount_price',
            field=models.IntegerField(),
        ),
    ]
