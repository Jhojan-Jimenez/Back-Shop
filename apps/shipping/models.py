from django.db import models


class Shipping(models.Model):
    class Meta:
        verbose_name = 'Shipping'
        verbose_name_plural = 'Shipping'
        ordering = ['price']

    name = models.CharField(max_length=255, unique=True)
    time_to_delivery = models.CharField(max_length=255)
    price = models.PositiveIntegerField()

    def __str__(self):
        return self.name
