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
    query = request.GET.get('q')
    excluded_ingredients = request.user.excluded_ingredients
    rejected_for = []  
    if query is not None:
        #if query is a number, and we will need a try/except here
        product = Product.objects.filter(upc=query)
        ingredients = product.ingredients.all()
        for ingredient in ingredients:
                if ingredient in excluded_ingredients:
                    rejected_for.append(ingredient)
    else:
        search_results = None
    return JsonResponse(rejected_for)

"""
Starting to wonder, though ... maybe I should make a classed based view for this instead so that I can assign a serializer to handle the response?  I'll know more once I've done some testing.
"""

def fuzzy_name(request, fuzzy):
	result = IngredientName.objects.filter(name__iexact = fuzzy)
	ingredient = get_object_or_404(Ingredient, names__in = result)
	return redirect(f'/api/ingredient/{ingredient.slug}/')
