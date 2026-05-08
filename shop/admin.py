from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_price', 'stock', 'date_added')
    list_filter = ('category', 'brand', 'date_added')
    search_fields = ('name', 'description')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'date_ordered', 'complete')
    list_filter = ('status', 'complete', 'date_ordered')

admin.site.register(Customer)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Feature)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(UpdateOrder)
admin.site.register(CheckoutDetail)
admin.site.register(Contact)