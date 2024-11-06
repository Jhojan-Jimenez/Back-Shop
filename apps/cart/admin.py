from django.contrib import admin

from .models import Cart, CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_items')
    list_display_links = ('id', 'user', )
    search_fields = ('user', )


admin.site.register(Cart, CartAdmin)


class CartItemsAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product',
                    'count')
    list_display_links = ('id', 'cart', 'product')
    list_editable = ('count', )


admin.site.register(CartItem, CartItemsAdmin)
