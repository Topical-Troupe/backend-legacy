from django.shortcuts import redirect, get_object_or_404
from .models import IngredientName, Product, Ingredient, User
#from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.http import JsonResponse

# Create your views here.
"""
First, I'm going to write this assuming that I am getting a UPC in the query.  
Will need a try/except for products that aren't in the db yet
"""
def search_products(request):
    name_q = request.GET.get('name')
    upc_q = request.GET.get('upc')
    print(name_q)
    common_set = ["bacitracin", "benzalkonium chloride", "cobalt chloride", "formaldehyde", "fragrence", "potassium dichromate", "nickel", "neomycin", "methylisothiazolinone", "methyldibromo glutaronitrile", "benzophenone 4"]
    common_names = IngredientName.objects.filter(name__in = common_set)
    common_allergens = Ingredient.objects.filter(names__in = common_names)
    excluded_ingredients = None
    response = {
        'count': 0,
        'results': []
    }
    if request.user.is_authenticated:
        excluded_ingredients = request.user.excluded_ingredients
    else:
        excluded_ingredients = common_allergens
    if name_q is not None:
        products = Product.objects.filter(name__contains = name_q)
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
        return redirect(f'/api/product/{upc_q}/')
    return JsonResponse(response)

def fuzzy_name(request, fuzzy):
	result = IngredientName.objects.filter(name__iexact = fuzzy)
	ingredient = get_object_or_404(Ingredient, names__in = result)
	return redirect(f'/api/ingredient/{ingredient.slug}/')
