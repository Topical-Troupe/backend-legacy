from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
import json
from rest_framework import routers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Lower
from .models import ExclusionProfile, Ingredient, IngredientName, Product, Tag, User
from .serializers import IngredientSerializer, ProductSerializer, ProfileSerializer, ProfileInitSerializer, UserSerializer
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
		if not request.User.is_authenticated:
			return HttpResponse(status = 401)
		if request.method == 'POST':
			if ingredient not in exclusions.all():
				exclusions.add(ingredient)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if ingredient in exclusions.all():
				exclusions.remove(ingredient)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)

	@action(detail = False, methods = ['POST'])
	def add(self, request):
		user = request.user
		restrictions = Ingredient.objects.filter(excluded_by = user)
		for ingredient in request.data['ingredients']:
			if len(restrictions.filter(names__name__iexact = ingredient)) > 0:
				#if this ingredient is already on the user restricted list
				print ("This item is already on your exclude list")
				continue
			elif len(Ingredient.objects.filter(name__iexact = ingredient)) > 0:
				#if this ingredient already exists as an object
				ingredient_to_add = Ingredient.objects.get(name__iexact = ingredient)
				user.excluded_ingredients.add(ingredient_to_add)
			elif len(IngredientName.objects.filter(name__iexact = ingredient)) > 0:
				#if this ingredient is a fuzzy name for and existing ingredient object
				ingredient_to_add = Ingredient.objects.get(names__name__iexact = ingredient) 
				print(ingredient_to_add)
				user.excluded_ingredients.add(ingredient_to_add)
				print(user.excluded_ingredients.all())
			else:
				#if this ingredient does not exist already
				new_ingredient = Ingredient.objects.create(name = ingredient)
				print("new ingredient found!")
				print(new_ingredient)
				print(user.excluded_ingredients.all())
				user.excluded_ingredients.add(new_ingredient)
				print(user.excluded_ingredients.all())
		return Response("Ingredient added!", status=status.HTTP_204_NO_CONTENT)
			
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
			excluded_ingredients = None
			if request.user.is_authenticated:
				setup_user(request)
				excluded_ingredients = request.user.excluded_ingredients.all()
			else:
				excluded_ingredients = User.get_default_exclusions()
			for ingredient in product.ingredients.all():
				ing_obj = {
					'name': ingredient.name,
					'slug': ingredient.slug,
					'description': ingredient.description,
					'names': []
				}
				for name in ingredient.names.all():
					ing_obj['names'].append(name.name)
				if ingredient in excluded_ingredients:
					response['violations'].append(ingredient.name)
				response['ingredient_list'].append(ing_obj)		
			return JsonResponse(response)	
		if not request.user.is_staff:
			return HttpResponse(status = 401)
		data = json.loads(request.body)
		if request.method == 'POST':
			for name in data['names']:
				product.ingredients.add(Ingredient.by_name(name))
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			for name in data['names']:
				product.ingredients.remove(Ingredient.by_name(name))
			return HttpResponse(status = 200)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def tags(self, request, upc):
		product = get_object_or_404(Product, upc = upc)
		if request.method == 'GET':
			response = []
			for tag in product.tags:
				response.append(tag.name)
			return JsonResponse(response)
		data = json.loads(request.body)
		tag = Tag.by_name(data['tags'])
		if request.method == 'POST':
			if tag not in product.tags.all():
				product.tags.add(tag)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if tag in product.tags.all():
				product.tags.remove(tag)
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
	@action(detail = True, methods = ['GET'])
	def own_profiles(self, request, username):
		user = get_object_or_404(User, username = username)
		serializer = ProfileSerializer(
			user.own_profiles,
			many = True,
			context = { 'context': request}
		)
		return Response(serializer.data)
router.register('user', UserViewSet)

class ProfileViewSet(viewsets.ModelViewSet):
	queryset = ExclusionProfile.objects.all()
	serializer_class = ProfileSerializer
	def create(self, request):
		data = request.data
		serializer = ProfileInitSerializer(data = data)
		if not serializer.is_valid():
			return HttpResponse(status = 400)
		profile = ExclusionProfile()
		profile.author = request.user
		profile.subscribers.add(request.user)
		profile.enabled.add(request.user)
		vdat = serializer.validated_data
		profile.name = vdat['name']
		if 'description' in vdat:
			profile.description = vdat['description']
		jdata = json.loads(data)
		for name in jdata['names']:
			ingredient = Ingredient.by_name(name)
			if ingredient is not None:
				profile.excluded_ingredients.add(ingredient)
		profile.save()
		return HttpResponse(status = 200)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def excludes(self, request, pk):
		profile = get_object_or_404(ExclusionProfile, pk = pk)
		if request.method == 'GET':
			response = {
				'count': 0,
				'ingredients': []
			}
			for ingredient in profile.excluded_ingredients.iterator():
				response['count'] += 1
				obj = {
					'name': ingredient.name,
					'slug': ingredient.slug,
					'names': []
				}
				for name in ingredient.names.iterator():
					obj['names'].append(name.name)
				response['ingredients'].append(obj)
			return JsonResponse(response)
		if not request.user == profile.author:
			return HttpResponse(status = 403)
		data = json.loads(request.data)
		if not 'names' in data:
			return HttpResponse(status = 400)
		if request.method == 'POST':
			for name in data['names']:
				ingredient = Ingredient.by_name(name)
				if ingredient is not None and ingredient not in profile.excluded_ingredients:
					profile.excluded_ingredients.add(ingredient)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			for name in data['names']:
				ingredient = Ingredient.by_name(name)
				if ingredient is not None and ingredient in profile.excluded_ingredients:
					profile.excluded_ingredients.remove(ingredient)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def subscribe(self, request, pk):
		if not request.user.is_authenticated:
			return HttpResponse(status = 403)
		profile = get_object_or_404(ExclusionProfile, pk = pk)
		subscribed = len(request.user.all_profiles.filter(pk = profile.pk)) > 0
		enabled = subscribed and len(request.user.profiles.filter(pk = profile.pk)) > 0
		if request.method == 'GET':
			response = {
				'subscribed': subscribed,
			}
			if subscribed:
				response['enabled'] = enabled
			return JsonResponse(response)
		if request.method == 'POST':
			if not subscribed:
				request.user.profiles.add(profile)
				request.user.all_profiles.add(profile)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if len(request.user.own_profiles.filter(pk = profile.pk)) > 0:
				return HttpResponse(status = 409)
			if subscribed:
				request.user.all_profiles.remove(profile)
				if enabled:
					request.user.profiles.remove(profile)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)
	@action(detail = True, methods = ['GET', 'POST', 'DELETE'])
	def enabled(self, request, pk):
		if not request.user.is_authenticated:
			return HttpResponse(status = 403)
		profile = get_object_or_404(ExclusionProfile, pk = pk)
		if request.method == 'GET':
			return self.subscribe(request, pk)
		subscribed = len(request.user.all_profiles.filter(pk = profile.pk)) > 0
		enabled = subscribed and len(request.user.profiles.filter(pk = profile.pk)) > 0
		if request.method == 'POST':
			if not enabled:
				request.user.profiles.add(profile)
			if not subscribed:
				request.user.all_profiles.add(profile)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if enabled:
				request.user.profiles.remove(profile)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)
router.register('profiles', ProfileViewSet)
