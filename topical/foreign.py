from json import loads as jsonload
from urllib.request import urlopen
from django.http import HttpResponse

from .models import Product

FAPI_URL = 'https://api.upcitemdb.com/prod/trial/lookup?upc='

def get_product_info(upc):
	url = f'{FAPI_URL}{upc}'
	return jsonload(urlopen(url).read().title())

def get_product_or_create(upc):
	item = Product.objects.filter(upc = upc)
	if len(item) != 0:
		return item
	else:
		response = get_product_info(upc)
		if response['Code'] != 'OK':
			return HttpResponse(status = 404)
		jso = response.json['Items'][0]
		item = Product()
		item.name = jso['Title']
		item.upc = upc
		# Uncomment this line if we want to add the brand to
		# the product model.
		#item.brand = jso['Brand']
		item.save()
		return item
