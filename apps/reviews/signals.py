from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review
from apps.product.models import Product
from django.db.models import Avg


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    # Obtener todas las reviews del producto actual
    product_reviews = Review.objects.filter(product=instance.product)

    # Calcular el promedio de los ratings si existen reviews
    if product_reviews.exists():
        average_rating = product_reviews.aggregate(Avg('rating'))[
            'rating__avg']
    else:
        average_rating = 5  # Si no hay reviews, el rating puede ser 0 o cualquier valor por defecto

    # Actualizar el rating del producto
    instance.product.rating = average_rating
    instance.product.save()
