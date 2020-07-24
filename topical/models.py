from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager

MAX_DESCRIPTION_LEN = 8192
MAX_NAME_LEN = 512

class Product(models.Model):
	name = models.CharField(max_length = MAX_NAME_LEN)
	description = models.TextField(max_length = MAX_DESCRIPTION_LEN, null = True)
	upc = models.CharField(max_length = 14, null = True, unique = True)
	image_url = models.CharField(max_length = MAX_DESCRIPTION_LEN, null =  True)

class Ingredient(models.Model):
	name = models.CharField(max_length = MAX_NAME_LEN)
	slug = models.CharField(max_length = MAX_NAME_LEN, unique = True)
	description = models.TextField(max_length = MAX_DESCRIPTION_LEN, blank = True)
	in_products = models.ManyToManyField(to = Product, symmetrical = True, related_name = 'ingredients')
	def save(self, *args, **kwargs):
		self.slug = self.generate_slug()
		basename = self.ensure_basename()
		super(Ingredient, self).save(*args, **kwargs)
		if basename is not None:
			basename.save()
	def __str__(self):
		return self.name
	def generate_slug(self):
		return (self.name.lower().replace(' ', '-'))
	def ensure_basename(self):
		test = self.names.filter(name = self.name)
		if len(test) == 0:
			basename = IngredientName()
			basename.name = self.name
			basename.ingredient = self
			return basename
	def by_name(name):
		names = IngredientName.objects.filter(name__iexact = name)
		res = Ingredient.objects.filter(names__in = names)
		if len(res) == 0:
			return None
		else:
			return res[0]

class IngredientName(models.Model):
	ingredient = models.ForeignKey(to = Ingredient, on_delete = models.SET_NULL, null = True, related_name = 'names')
	name = models.CharField(max_length = MAX_NAME_LEN, unique = True)
	def __str__(self):
		return self.name

DEFAULT_EXCLUSIONS = ["bacitracin", "benzalkonium chloride", "cobalt chloride", "formaldehyde", "fragrence", "potassium dichromate", "nickel", "neomycin", "methylisothiazolinone", "methyldibromo glutaronitrile", "benzophenone 4"]

class UserManager(BaseUserManager):
	def get_default_exclusions():
		common_names = IngredientName.objects.filter(name__in = DEFAULT_EXCLUSIONS)
		return Ingredient.objects.filter(names__in = common_names).all()
	def create(self, *args, **kwargs):
		output = super(UserManager, self).create(*args, **kwargs)
		for ingredient in UserManager.get_default_exclusions():
			output.excluded_ingredients.add(ingredient)
		return output

class User(AbstractUser):
	objects = UserManager()
	excluded_ingredients = models.ManyToManyField(to = Ingredient, symmetrical = True, related_name = 'excluded_by', blank = True)
