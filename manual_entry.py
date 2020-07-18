import requests
site = input('enter the URL to send the requests to').trim()
if not site.endswith('/'):
	site += '/'

endpoint = {
	'ingredient': (f'{site}api/product/')
}

def post_ingredient():
	pass

def post_name():
	pass

def post_product():
	pass

def main():
	print('i for ingredient, n for ingredient name, p for product')
	type = input('type: ').lower().trim()

	if type == 'i':
		post_ingredient()
	elif type == 'n':
		post_name()
	elif type == 'p':
		post_product()

	request = requests.post()
