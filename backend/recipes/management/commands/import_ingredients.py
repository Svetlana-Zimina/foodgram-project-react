import csv
import pathlib
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

path = Path(pathlib.Path.home(), 'data', 'ingredients.csv')


def import_data():
    """Чтение файла CSV и создания экземпляров модели"""
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Ingredient.objects.create(
                field1=row['name'],
                field2=row['measurement_unit'],
            )


class Command(BaseCommand):
    help = 'Импорт ингридиентов в базу данных'

    def handle(self, *args, **options):
        import_data()
        self.stdout.write(
            self.style.SUCCESS('Ингридиенты успешно загружены в базу')
        )
