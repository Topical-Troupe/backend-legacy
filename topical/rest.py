from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Lower
from .models import Ingredient, Product, User
from .serializers import IngredientSerializer, ProductSerializer, UserSerializer
from .views import setup_user

router = routers.DefaultRouter()

class IngredientViewSet(viewsets.ModelViewSet):
	queryset = Ingredient.objects.all()
	serializer_class = IngredientSerializer
	lookup_field = 'slug'
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def exclude(self, request, slug):
		ingredient = get_object_or_404(Ingredient, slug = slug)
		exclusions = None
		if request.User.is_authenticated:
			exclusions = request.user.excluded_ingredients
		else:
			exclusions = User.get_default_exclusions()
		if request.method == 'GET':
			is_excluded = ingredient in request.user.excluded_ingredients.all()
			return JsonResponse({ 'excluded': is_excluded })
		if request.method == 'POST':
			if ingredient not in exclusions.all():
				exclusions.add(ingredient)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if ingredient in exclusions.all():
				exclusions.remove(ingredient)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)
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
				setup_user(request)

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
	@action(detail = False, methods = ['GET'])
	def exclusions(self, request):
		exclusions = None
		if request.user.is_authenticated:
			exclusions = request.user.excluded_ingredients.all()
		else:
			exclusions = User.get_default_exclusions()
		response = {
			'count': len(exclusions),
			'items': []
		}
		for ingredient in exclusions:
			json_ing = {
				'name': ingredient.name,
				'slug': ingredient.slug,
				'names': []
			}
			for name in ingredient.names.all():
				json_ing['names'].append(name)
			response['items'].append(json_ing)
		return JsonResponse(response)
router.register('user', UserViewSet)
