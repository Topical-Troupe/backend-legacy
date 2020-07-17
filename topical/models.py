from django.db import models
from django.contrib.models import AbstractUser

class Ingredient(models.Model):
	pass

class IngredientName(models.Model):
	ingredient = models.ForeignKey(to = Ingredient, on_delete = models.CASCADE, related_name = 'names')

class User(AbstractUser):
	excluded_ingredients = models.ManyToManyField(to = Ingredient, symmetrical = True, related_name = 'excluded_by')
