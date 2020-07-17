from django.db import models
from django.contrib.auth.models import AbstractUser

MAX_DESCRIPTION_LEN = 8192
MAX_INGREDIENT_LEN = 512

class Ingredient(models.Model):
	description = models.TextField(max_length = MAX_DESCRIPTION_LEN)

class IngredientName(models.Model):
	ingredient = models.ForeignKey(to = Ingredient, on_delete = models.CASCADE, related_name = 'names')
	name = models.CharField(max_length = MAX_INGREDIENT_LEN)
	def __repr__(self):
		return self.name

class User(AbstractUser):
	excluded_ingredients = models.ManyToManyField(to = Ingredient, symmetrical = True, related_name = 'excluded_by')
