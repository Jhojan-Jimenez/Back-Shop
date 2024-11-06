from django.db import models
from django.utils import timezone
from apps.category.models import Category
from django.core.validators import MinValueValidator, MaxValueValidator


class Product(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='photos/%Y/%m/')
    description = models.TextField()
    price = models.PositiveIntegerField()
    compare_price = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)
    rating = models.DecimalField(
        # Un máximo de 3 dígitos en total (incluyendo el dígito decimal)
        max_digits=3,
        decimal_places=1,  # Máximo 1 dígito decimal
        default=5,         # Valor por defecto es 0

    )

    class Meta:
        ordering = ['date_created']

    def get_thumbnail(self):
        if self.photo:
            return self.photo.url
        return ''

    def __str__(self):
        return self.name
