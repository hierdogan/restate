from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Address, Property, PropertyOwner, PropertyTransaction, PropertySale, PropertyRental

admin.site.register(User)
admin.site.register(Address)
admin.site.register(Property)
admin.site.register(PropertyOwner)
admin.site.register(PropertyTransaction)
admin.site.register(PropertySale)
admin.site.register(PropertyRental)
