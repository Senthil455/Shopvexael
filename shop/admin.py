from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'discount_price', 'stock', 'is_featured', 'is_trending')
    list_filter = ('category', 'brand', 'is_featured', 'is_trending')
    search_fields = ('name', 'description', 'sku')

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'category')

class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'date_ordered', 'complete')
    list_filter = ('status', 'complete', 'date_ordered')

class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'stock', 'additional_price')

admin.site.register(Customer)
admin.site.register(Seller)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(Coupon)
admin.site.register(Feature)
admin.site.register(Review)
admin.site.register(Wishlist)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(UpdateOrder)
admin.site.register(CheckoutDetail)
admin.site.register(Contact)