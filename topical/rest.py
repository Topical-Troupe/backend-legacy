from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Lower
from .models import Ingredient, Product, User
from .serializers import IngredientSerializer, ProductSerializer, UserSerializer

router = routers.DefaultRouter()

class IngredientViewSet(viewsets.ModelViewSet):
	queryset = Ingredient.objects.all()
	serializer_class = IngredientSerializer
	lookup_field = 'slug'
router.register('ingredient', IngredientViewSet)

class ProductViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.all()
	serializer_class = ProductSerializer
	lookup_field = 'upc'
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def ingredients(self, request, upc):
		product = get_object_or_404(Product, upc = upc)
		if request.method == 'GET':
			#response = {
			#	'violations': [],
			#	'ingredient_list': []
			#}
			serializer = IngredientSerializer(
				product.ingredients.all(),
				many = True,
				context = { 'context': request }
			)
			if request.user.is_authenticated:
				if len(request.user.excluded_ingredients.all()) == 0:
					for ingredient in User.get_default_exclusions():
						request.user.excluded_ingredients.add(ingredient)
				excluded_ingredients = request.user.excluded_ingredients

			else:
				excluded_ingredients = User.get_default_exclusions()
				print("anonymous user")

			fuzzy_names = []
			for ingredient in excluded_ingredients.all():
				names = ingredient.names.all()
				lc_names = names.annotate(name_lower=Lower('name'))
				for name in lc_names:
					fuzzy_names.append(name.name_lower)

			lower_ingredients = []
			ingredients = product.ingredients.all()
			lc_ingredients = ingredients.annotate(name_lower=Lower('name'))
			for ingredient in lc_ingredients:
				lower_ingredients.append(ingredient.name_lower)
			print("lower case ingredients")
			print(lower_ingredients)

			flagged_ingredients = []

			for ingredient in lower_ingredients:
				print("ingredient")
				print(ingredient)
				if ingredient in fuzzy_names:
					print("FOUND ONE!!!!!!!!!!!!!!!!!!!")
					print(ingredient)
					flagged_ingredients.append(ingredient)
					#response['violations'].append(ingredient)
			print("Flagged:")
			print(flagged_ingredients)
			ingredient_list = product.ingredients.all()
			print("ingredient list")
			print(ingredient_list)
			violations = product.ingredients.filter(name__in = fuzzy_names)
			print("violations:")
			print(violations)
			warning = IngredientSerializer(
				excluded_ingredients.all(), many = True, context = { 'context': request })
			return Response(warning.data)

		if request.method == 'POST':
			if not request.user.is_staff:
				return HttpResponse(status = 401)
			data = json.loads(request.body)
			for name in data['names']:
				product.ingredients.add(Ingredient.by_name(name))
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if not request.user.is_staff:
				return HttpResponse(status = 401)
			data = json.loads(request.body)
			for name in data['names']:
				product.ingredients.remove(Ingredient.by_name(name))
			return HttpResponse(status = 200)
router.register('product', ProductViewSet)

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'username'
	@action(detail = False, methods = ['GET'])
	def me(self, request):
		if not request.user.is_authenticated:
			return HttpResponse(status = 404)
		serializer = UserSerializer(
			request.user,
			many = False,
			context = { 'context': request }
		)
		return Response(serializer.data)
router.register('user', UserViewSet)
