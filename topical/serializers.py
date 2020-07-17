from rest_framework import serializers

from .models import Ingredient, User

class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ['username', 'first_name', 'last_name', 'excluded_ingredients']

class IngredientSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = Ingredient
		fields = ['names', 'description']
