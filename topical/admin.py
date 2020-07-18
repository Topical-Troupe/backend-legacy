from django.contrib import admin

from .models import Ingredient, Product, User

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Ingredient)