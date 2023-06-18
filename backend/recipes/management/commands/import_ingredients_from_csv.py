from csv import reader

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/ingredients.csv', 'r',
                encoding='UTF-8'
        ) as ingredients:
            ingredients_list = []
            for row in reader(ingredients):
                if len(row) == 2:
                    ingredients_list.append(
                        Ingredient(
                            name=row[0],
                            measurement_unit=row[1],
                        )
                    )
            Ingredient.objects.bulk_create(ingredients_list)
