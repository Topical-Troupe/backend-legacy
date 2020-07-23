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
	slug = serializers.ReadOnlyField()
	names = RelatedNameSerializer(read_only = False, many = True, required = False, default = [])

	def create(self, validated_data):
		names_data = validated_data.pop('names',[])
		ingredient = Ingredient.objects.create(**validated_data)
		for name_data in names_data:
			if len(IngredientName.objects.filter(name__iexact = name_data.get('name'))):
				continue
			IngredientName.objects.create(ingredient=ingredient, **name_data)
		return ingredient

	#def update(self, instance, validated_data):
	#	ingredient = instance
	#	names_data = validated_data.pop('names', [])
	#	for key, value in validated_data.items():
	#		setattr(ingredient, key, value)
	#	ingredient.save()
	#	for name_data in names_data:
	#		if len(IngredientName.objects.filter(name__iexact = name_data.get('name'))):
	#			continue
	#		IngredientName.objects.create(ingredient=ingredient, **name_data)
	#	return ingredient

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
