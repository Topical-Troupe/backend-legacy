from rest_framework import serializers

from .models import Ingredient, IngredientName, Product, User

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'excluded_ingredients']

class RelatedNameSerializer(serializers.ModelSerializer):
	class Meta:
		model = IngredientName
		fields = ['name']

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
	#slug = serializers.ReadOnlyField()
	names = RelatedNameSerializer(read_only = False, many = True, required = False, default = [])
	class Meta:
		model = Ingredient
		fields = ['name', 'slug', 'names', 'description']

class IngredientNameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = IngredientName
		fields = ['name', 'ingredient']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
	ingredients = IngredientSerializer(read_only = True, many = True, required = False, default = [])
	class Meta:
		model = Product
		fields = ['name', 'upc', 'description', 'ingredients'] 
