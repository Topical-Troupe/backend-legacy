from rest_framework import serializers

from .models import Ingredient, IngredientName, Product, User

class UserSerializer(serializers.ModelSerializer):
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

	class Meta:
		model = Ingredient
		fields = ['name', 'slug', 'names', 'description']	
	
	def create(self, validated_data):
		names_data = validated_data.pop('names',[])
		ingredient = Ingredient.objects.create(**validated_data)
		for name_data in names_data:
			if len(IngredientName.objects.filter(name__iexact = name_data.get('name'))):
				continue
			IngredientName.objects.create(ingredient=ingredient, **name_data)
		return ingredient

	def update(self, instance, validated_data):
		ingredient = instance
		names_data = validated_data.pop('names', [])
		for key, value in validated_data.items():
			setattr(ingredient, key, value)
		ingredient.save()
		for name_data in names_data:
			if len(IngredientName.objects.filter(name__iexact = name_data.get('name'))):
				continue
			IngredientName.objects.create(ingredient=ingredient, **name_data)
		return ingredient

class IngredientNameSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = IngredientName
		fields = ['name', 'ingredient']

class ProductSerializer(serializers.HyperlinkedModelSerializer):
	ingredients = IngredientSerializer(many=True, required=False)

	def create(self, validated_data):
		ingredients_data = validated_data.pop('ingredients', [])
		product = Product.objects.create(**validated_data)
		for ingredient_data in ingredients_data:
			if len(IngredientName.objects.filter(name__iexact = ingredient_data.get('name'))):
				print("duplicate")
				continue
			ingredient_name = ingredient_data.get('name')
			new_ingredient = Ingredient.objects.create(name=ingredient_name)
			product.ingredients.add(new_ingredient)
		return product

	class Meta:
		model = Product
		fields = ['name', 'upc', 'image_url', 'description', 'ingredients'] 
