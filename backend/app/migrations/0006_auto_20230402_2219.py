# Generated by Django 3.2.17 on 2023-04-02 19:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_ingredientrecipe_amount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'default_related_name': 'ingredients_recipes', 'verbose_name': 'Подсчет ингредиентов', 'verbose_name_plural': 'Подсчеты ингредиентов'},
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_recipes', to='app.ingredient'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_recipes', to='app.recipe'),
        ),
    ]
