from django.contrib import admin
from django import forms

from apps.product.models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'compare_price',
                    'price', 'quantity', 'sold', 'rating')
    list_display_links = ('id', 'name', )
    list_filter = ('category', )
    list_editable = ('compare_price', 'price', 'quantity', )
    search_fields = ('name', 'description', )

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new products
            Product.objects.create_product(
                name=obj.name,
                photo=request.FILES.get('photo'),
                description=obj.description,
                price=obj.price,
                compare_price=obj.compare_price,
                category=obj.category,
                quantity=obj.quantity,
                sold=obj.sold,
                rating=obj.rating
            )
        else:
            super().save_model(request, obj, form, change)

