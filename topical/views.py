from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from .models import IngredientName, Product, Ingredient, User
from django.http import JsonResponse

from .foreign import get_product_or_create

# Create your views here.
"""
First, I'm going to write this assuming that I am getting a UPC in the query.  
Will need a try/except for products that aren't in the db yet
"""
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
        excluded_ingredients = request.user.excluded_ingredients
    else:
        excluded_ingredients = User.get_default_exclusions()
    if name_q is not None:
        products = Product.objects.filter(name__icontains = name_q)
        response['count'] = len(products)
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
