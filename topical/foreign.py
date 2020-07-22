from json import loads as jsonload
from urllib.request import urlopen
from django.http import HttpResponse

from .models import Product

FAPI_URL = 'https://api.upcitemdb.com/prod/trial/lookup?upc='

def get_product_info(upc):
	url = f'{FAPI_URL}{upc}'
	print(url)
	return jsonload(urlopen(url).read().title())

def get_product_or_create(upc):
	item = Product.objects.filter(upc = upc)
	print(item, upc)
	if len(item) == 0:
		if len(upc) == 13 and upc[0] == '0':
			item = Product.objects.filter(upc = upc[1:])
		elif len(upc) == 12:
			item = Product.objects.filter(upc = f'0{upc}')
	if len(item) != 0:
		return item
	else:
		response = get_product_info(upc)
		if response['Code'] != 'Ok' or len(response['Items']) == 0:
			return HttpResponse(status = 404)
		jso = response['Items'][0]
		item = Product()
		item.name = jso['Title']
		if len(jso["Images"]) != 0:
			item.image_url = jso["Images"][0]
		item.upc = upc
		# Uncomment this line if we want to add the brand to
		# the product model.
		#item.brand = jso['Brand']
		item.save()
		print(item)
		return item
