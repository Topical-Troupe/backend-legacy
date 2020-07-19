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
	if len(item) == 0:
		response = get_product_info(upc)
		if response.status_code != 200:
			return HttpResponse(status = response.status_code)
		item = Product()
		item.name = response.json['title']
		raw_ing = response.json['description']
		return item
