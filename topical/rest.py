from django.db.models import Count
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
		exclusions = request.user.get_excluded()
		if request.method == 'GET':
			is_excluded = ingredient in request.user.excluded_ingredients.all()
			return JsonResponse({ 'excluded': is_excluded })
		data = json.loads(request.body)
		profile = None
		if 'profile' in data:
			profile = get_object_or_404(ExclusionProfile, pk = data['profile'])
		if profile is None:
			return HttpResponse(status = 400)
		if not request.user.is_authenticated:
			return HttpResponse(status = 401)
		if request.method == 'POST':
			if ingredient not in exclusions:
				ingredient.excluded_by.add(profile)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			if ingredient in exclusions:
				ingredient.excluded_by.remove(profile)
			return HttpResponse(status = 200)
		return HttpResponse(status = 405)

	@action(detail = False, methods = ['POST'])
	def add(self, request):
		for name in request.data['ingredients']:
			ingredient = Ingredient.by_name(name)
			if ingredient is None:
				new_ingredient = Ingredient.objects.create(name = ingredient)
				print("new ingredient found!")
				print(new_ingredient)
			if hasattr(request.data, 'profile_pk'):
				profile = request.data['profile_pk']
				if profile.author != request.user:
					print("The user doesn't own this list.")
					continue
				if ingredient in profile.excluded_ingredients.all():
					#if this ingredient is already on the user restricted list
					print ("This item is already in this list")
					continue
				else:
					profile.excluded_ingredients.add(ingredient)	
		return Response("Ingredient added!", status=status.HTTP_204_NO_CONTENT)
	@action(detail = True, methods = ['GET'])
	def stats(self, request, slug):
		ingredient = get_object_or_404(Ingredient, slug = slug)
		response = {
			'exclusion_count': 0,
			'top_lists': []
		}
		for profile in ingredient.excluded_by.annotate(exc_count = Count('excluded_by')).order_by('-exc_count').iterator():
			response['exclusion_count'] += 1
			if len(response['top_lists']) < 5:
				response['top_lists'].append(profile)
		return JsonResponse(response)
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
				'name': product.name,
				'image_url': product.image_url,
				'violations': [],
				'ingredient_list': []
			}
			excluded_ingredients = request.user.get_excluded()
			for ingredient in product.ingredients.iterator():
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
			if tag not in product.tags.iterator():
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
		exclusions = request.user.get_excluded()
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
				if ingredient is not None and ingredient not in profile.excluded_ingredients.iterator():
					profile.excluded_ingredients.add(ingredient)
			return HttpResponse(status = 200)
		if request.method == 'DELETE':
			for name in data['names']:
				ingredient = Ingredient.by_name(name)
				if ingredient is not None and ingredient in profile.excluded_ingredients.iterator():
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
