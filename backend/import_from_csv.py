import os

from django.core.management.base import BaseCommand, CommandError


DICT = {
    'recipes_ingredient': 'recipes_ingredients.csv',
}


class Command(BaseCommand):
    help = u'Импортируем данные из файлов CSV в BD'

    def handle(self, *args, **kwargs):
        try:
            for bd, file in DICT.items():
                os.system(
                    f'sqlite3 ./db.sqlite3 ".mode csv"  ".import'
                    f' static/data/{file} {bd}"')
        except Exception as error:
            CommandError(error)
