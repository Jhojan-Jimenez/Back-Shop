from django.db import models


class FixedPriceCoupon(models.Model):
    name = models.CharField(max_length=255, unique=True)
    discount_price = models.IntegerField()

    def __str__(self):
        return self.name


class PercentageCoupon(models.Model):
    name = models.CharField(max_length=255, unique=True)
    discount_percentage = models.IntegerField()

    def __str__(self):
        return self.name
