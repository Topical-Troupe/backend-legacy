from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

			fuzzy_names = []
			for ingredient in excluded_ingredients.all():
				names = ingredient.names.all()
				for name in names:
					fuzzy_names.append(name)
			violations = product.ingredients.filter(name__in = fuzzy_names)
			warning = IngredientSerializer(
				violations.all(), many = True)
			return Response(serializer.data, warning.data)
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
