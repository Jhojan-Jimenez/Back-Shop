from django.db import models
from django.utils import timezone
from apps.category.models import Category
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .utils import upload_image_to_api


class ProductManager(models.Manager):
    def create_product(self, name, photo, description, price, compare_price, category, quantity, sold, rating):
        try:
            product = self.create(name=name,    description=description, price=price,
                                  compare_price=compare_price, category=category, quantity=quantity, sold=sold, rating=rating)

            # Process the photo
            if photo:
                temp_file = ContentFile(photo.read())
                response = upload_image_to_api(
                    temp_file, name=name, description=description)

                if response.status_code in [200, 201]:
                    product.photo = response.json().get('data').get('link')
                    product.save()

            return product
        except Exception as e:
            print(e)


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
        max_digits=3,
        decimal_places=1,
        default=5,
    )
    objects = ProductManager()

    class Meta:
        ordering = ['date_created']

    def get_thumbnail(self):
        if self.photo:
            return self.photo.url
        return ''

    def __str__(self):
        return self.name
