from django.db import models
from django.contrib.auth.models import AbstractUser

MAX_DESCRIPTION_LEN = 8192
MAX_NAME_LEN = 512

class Product(models.Model):
	name = models.CharField(max_length = MAX_NAME_LEN)
	description = models.TextField(max_length = MAX_DESCRIPTION_LEN, null = True)

class Ingredient(models.Model):
	name = models.CharField(max_length = MAX_NAME_LEN)
	description = models.TextField(max_length = MAX_DESCRIPTION_LEN, null = True)
	in_products = models.ForeignKey(to = Product, on_delete = models.SET_NULL, null = True, related_name = 'ingredients')

class IngredientName(models.Model):
	ingredient = models.ForeignKey(to = Ingredient, on_delete = models.SET_NULL, null = True, related_name = 'names')
	name = models.CharField(max_length = MAX_NAME_LEN)
	def __repr__(self):
		return self.name

class User(AbstractUser):
	excluded_ingredients = models.ManyToManyField(to = Ingredient, symmetrical = True, related_name = 'excluded_by')
