from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404

from .models import IngredientName, Product, Ingredient, Tag, User
from .foreign import get_product_or_create

def setup_user(request):
    user = User.objects.get(username = request.user.username)
    if not user.is_setup:
        print('setting up user')
        for ingredient in User.get_default_exclusions():
            user.excluded_ingredients.add(ingredient)
        user.is_setup = True
        user.save()
    return HttpResponse(status = 200)

def search_products(request):
    name_q = request.GET.get('name')
    upc_q = request.GET.get('upc')
    print(upc_q)
    excluded_ingredients = None
    response = {
        'count': 0,
        'results': []
    }
    if request.user.is_authenticated:
        setup_user(request)
        excluded_ingredients = request.user.excluded_ingredients
    else:
        excluded_ingredients = User.get_default_exclusions()
    if name_q is not None:
        tags = Tag.objects.filter(name__in = name_q.split())
        products = Product.objects.filter(
            Q(tags__in = tags) |
            Q(name__search = name_q) |
            Q(description__search = name_q) |
            Q(ingredients__names__name__search = name_q)
        )
        response['count'] = len(products.all())
        for product in products.all():
            obj = {
                'upc': product.upc,
                'name': product.name,
                'violations': []
            }
            ingredients = product.ingredients.all()
            for n in range(len(ingredients)):
                ingredient = ingredients[n]
                if ingredient in excluded_ingredients.all():
                    violation_data = {
                        'slug': ingredient.slug,
                        'description': ingredient.description,
                        'names': []
                    }
                    for name in ingredient.names:
                        violation_data['names'].append(name.name)
                    obj['violations'].append(violation_data)
            response['results'].append(obj)
    if upc_q is not None:
        product = get_product_or_create(upc_q)
        if type(product) is HttpResponse:
            return redirect(f'/api/product/notfound/{upc_q}/')
        return redirect(f'/api/product/{upc_q}/')
    return JsonResponse(response)

def fuzzy_name(request, fuzzy):
	result = IngredientName.objects.filter(name__iexact = fuzzy)
	ingredient = get_object_or_404(Ingredient, names__in = result)
	return redirect(f'/api/ingredient/{ingredient.slug}/')

def product_404(request, upc):
    if len(upc) < 12 or len(upc) > 13:
        return HttpResponse(status = 406)
    if len(Product.objects.filter(upc = upc)) != 0:
        return HttpResponse(status = 409)
    if request.method == 'GET':
        return JsonResponse({
            'info': 'That product was not found! Please POST it with at least the name and UPC included.',
            'upc': {upc},
            'url': '/api/product/'
        })
    else:
        return HttpResponse(status = 405)
