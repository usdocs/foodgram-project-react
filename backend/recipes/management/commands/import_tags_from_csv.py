from csv import reader

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Load ingredients data from csv-file to DB.'

    def handle(self, *args, **kwargs):
        with open(
                'recipes/data/tags.csv', 'r',
                encoding='UTF-8'
        ) as tags:
            tags_list = []
            for row in reader(tags):
                if len(row) == 3:
                    tags_list.append(
                        Tag(
                            name=row[0],
                            color=row[1],
                            slug=row[2]
                        )
                    )
            Tag.objects.bulk_create(tags_list)
