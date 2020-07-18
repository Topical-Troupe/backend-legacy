from rest_framework import serializers

from .models import Ingredient, Product, User

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'excluded_ingredients']

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
	slug = serializers.ReadOnlyField()
	names = serializers.ReadOnlyField(source = 'names.all')
	class Meta:
		model = Ingredient
		fields = ['name', 'slug', 'names', 'description']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
	ingredients = IngredientSerializer(read_only = True, many = True, required = False, default = [])
	class Meta:
		model = Product
		fields = ['name', 'description', 'ingredients']