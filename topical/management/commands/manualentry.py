from django.core.management.base import BaseCommand, CommandError
from topical.models import Product, Ingredient, IngredientName

TYPE_SET = ['i', 'n', 'p']

class Command(BaseCommand):
	help = 'Manually enter data to the database'
	def add_arguments(self, parser):
		pass
	def handle(self, *args, **options):
		print('i = ingredient; n = ingredientname; p = product')
		typeof = None
		while typeof is None or not typeof in TYPE_SET:
			typeof = input('Input type (i/n/p): ')
		if typeof == 'i':
			name = None
			while name is None:
				name = input('ingredient name: ')
				if len(Ingredient.objects.filter(name__iexact = name)):
					print(f'{name} is already an ingredient!')
					name = None
			descript = input('Description: ')
			ingredient = Ingredient()
			ingredient.name = name
			ingredient.description = descript
			ingredient.save()
			print('successfully added!')
		if typeof == 'n':
			ingredient = None
			while ingredient is None:
				fuzzy_name = None
				res = None
				while fuzzy_name is None:
					fuzzy_name = input('ingredient name: ')
					res = IngredientName.objects.filter(name__iexact = fuzzy_name)
					if len(res) == 0:
						fuzzy_name = None
						res = res.all()
				ingredient = Ingredient.objects.filter(names__in = res)
				if len(ingredient) == 0:
					ingredient = None
					print('ingredient not found!')
					if not input('continue (y/n)? ').lower().strip() == 'y':
						break
				else:
					ingredient = ingredient[0]
			if ingredient is not None:
				item = IngredientName()
				name = None
				while name is None:
					name = input('New name: ')
					if len(IngredientName.objects.filter(name = name)) != 0:
						print(f'{name} is already used!')
						name = None
				item.name = name
				item.ingredient = ingredient
				item.save()
				print('successfully added!')
		if typeof == 'p':
			name = None
			product = None
			while name is None:
				name = input('Name: ')
				res = Product.objects.filter(name_iexact = name)
				if len(res) != 0:
					cont = input(f'A product called {name} already exists! Did you want to add ingredients (y/n)? ').lower().strip()
					if cont != 'y':
						name = None
			if product is not None:
				print('currently unimplemented, sorry :(')
			else:
				product = Product()
				product.name = name
				print('currently unimplemented, sorry :(')
		if input('Enter more (y/n)? ').lower().strip() == 'y':
			self.handle(*args, **options)
