from django.shortcuts import render, get_object_or_404
from .models import Product, Ingredient, User
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
    common_allergens = ["bacitracin", "benzalkonium chloride", "cobalt chloride", "formaldehyde", "fragrence", "potassium dichromate", "nickel", "neomycin", "methylisothiazolinone", "methyldibromo glutaronitrile"]
    excluded_ingredients = request.user.excluded_ingredients
    rejected_for = []  
    if query is not None:
        product = Product.objects.filter(upc=query)
        ingredients = product.ingredients.all()
        #all_ingredients = ingredients
        if request.user.is_authenticated:
            #if query is a number, and we will need a try/except here
            for ingredient in ingredients:
                if ingredient in excluded_ingredients:
                    rejected_for.append(ingredient)
        else:
            for ingredient in ingredients:
                if ingredient in common_allergens:
                    rejected_for.append(ingredient)

    else:
        rejected_for = None
    return JsonResponse(rejected_for)

"""
Starting to wonder, though ... maybe I should make a class based view for this instead so that I can assign a serializer to handle the response?  I'll know more once I've done some testing.
"""