# Generated by Django 3.2.3 on 2023-09-04 08:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_recipe_is_favorited_recipe_is_in_shopping_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='is_favorited',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='is_in_shopping_cart',
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('author', 'name'), name='unique recipe name'),
        ),
    ]
