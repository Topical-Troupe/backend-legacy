from django.contrib import admin

from .models import ExclusionProfile, Ingredient, Product, Tag, User

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(ExclusionProfile)
