from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    # Usar un campo CharField para devolver la URL de la imagen en lugar de ImageField
    photo = serializers.CharField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'photo',
            'description',
            'price',
            'compare_price',
            'category',
            'quantity',
            'sold',
            'date_created',
            'rating',
            'get_thumbnail'
        ]

    def get_photo(self, obj):
        # Asegúrate de que la URL esté correctamente formateada antes de devolverla
        photo_url = obj.photo
        if photo_url.startswith("/"):
            photo_url = photo_url[1:]  # Eliminar la barra inicial
        if not photo_url.startswith("http"):
            # Asegurarse de que tenga el protocolo adecuado
            photo_url = f"https:{photo_url}"
        return photo_url
