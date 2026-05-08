from django.contrib import admin
from . models import *

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Feature)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CheckoutDetail)
admin.site.register(UpdateOrder)
admin.site.register(Contact)