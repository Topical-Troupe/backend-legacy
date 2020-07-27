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
			response = {
				'violations': [],
				'ingredient_list': []
			}
			"""
			Set user restrictions: can be removed in production as it is redundant with views.py/search_products
			"""
			if request.user.is_authenticated:
				if len(request.user.excluded_ingredients.all()) == 0:
					for ingredient in User.get_default_exclusions():
						request.user.excluded_ingredients.add(ingredient)
				excluded_ingredients = request.user.excluded_ingredients

			else:
				excluded_ingredients = User.get_default_exclusions()
			"""
			Set all excluded fuzzy names to lower case and create a list for comparison
			"""
			fuzzy_names = []
			for ingredient in excluded_ingredients.all():
				names = ingredient.names.all()
				lc_names = names.annotate(name_lower=Lower('name'))
				for name in lc_names:
					fuzzy_names.append(name.name_lower)
			"""
			Set all product ingredient names to lower case and create a list for comparison
			"""
			lower_ingredients = []
			ingredients = product.ingredients.all()
			lc_ingredients = ingredients.annotate(name_lower=Lower('name'))
			for ingredient in lc_ingredients:
				lower_ingredients.append(ingredient.name_lower)
			"""
			Compare excluded items to product ingredients and make a list of violations
			"""
			for ingredient in lower_ingredients:
				if ingredient in fuzzy_names:
					response['violations'].append(ingredient)
			"""
			Create objects to be returned as full ingredient list
			"""
			ingredients = product.ingredients.all()
			for ingredient in ingredients:
				obj = {
					'name': ingredient.name,
					'slug': ingredient.slug,
					'description': ingredient.description
				}
				response['ingredient_list'].append(obj)			
			return JsonResponse(response)
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
