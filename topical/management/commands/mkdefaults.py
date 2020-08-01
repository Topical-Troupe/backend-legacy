from django.core.management.base import BaseCommand, CommandError
from topical.models import DEFAULT_EXCLUSIONS, ExclusionProfile, Ingredient, IngredientName, User

class Command(BaseCommand):
	help = 'Sets up the default exclusion list with its ingredients.'
	def add_arguments(self, parser):
		pass
	def handle(self, *args, **options):
		admin = User.objects.filter(username = 'admin')
		if len(admin) != 1:
			print('admin user is not set up correctly')
			return
		else:
			admin = admin[0]
		profile = ExclusionProfile.objects.filter(pk = 1)
		if len(profile) == 0:
			profile = ExclusionProfile()
			profile.save()
		else:
			profile = profile[0]
		profile.name = 'Default'
		profile.description = "Topical's default exclusion list based on the Mayoclinic's list of common irritants."
		profile.author = admin
		profile.save()
		for name in DEFAULT_EXCLUSIONS:
			ingredient = Ingredient.by_name(name)
			if ingredient is None:
				ingredient = Ingredient()
				ingredient.name = name
				ingredient.description = ''
				ingredient.save()
			if ingredient not in profile.excluded_ingredients.all():
				ingredient.excluded_by.add(profile)
		profile.save()
		print('successfully set up defaults!')
			