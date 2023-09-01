import csv

from django.core.management.base import BaseCommand
from foodgram_backend.settings import CSV_DIR
from recipes.models import Ingredient


def import_data():
    """Чтение файла CSV и создания экземпляров модели"""
    with open(f'{CSV_DIR}/ingredients.csv') as csvfile:
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
