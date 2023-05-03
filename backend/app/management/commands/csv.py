import csv
import pathlib
from pathlib import Path

from django.core.management.base import BaseCommand

from ..models import Ingredient

# dir_path = pathlib.Path('c:/', 'Dev', 'foodgram-project-react')
path = Path('/app', 'data', 'ingredients.csv')


class Command(BaseCommand):
    help = 'Load data from csc_file'

    def handle(self, *args, **options):
        with open(
                path,
                'r',
                newline='',
                encoding='utf-8'
                ) as ingredients_file:
            file_reader = csv.reader(ingredients_file, delimiter=",")
            for row in file_reader:
                Ingredient.objects.create(name=f'{row[0]}', measurement_unit=f'{row[1]}')
