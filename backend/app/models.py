from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Tag(models.Model):
    """Класс тегов рецептов."""

    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Класс ингредиентов."""

    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Класс рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/', null=False, blank=False)
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        db_constraint=False
    )
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        default_related_name = 'recipe'
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    """Класс связующая таблица ингредиентов и рецептов."""
    """Эта таблица, связующая для рецепта и ингредиентов, 
    в рецепте у меня связь ManyToManyField, это неявно создает еще одну таблицу. 
     Так что я реализую это явно - доп таблицу (IngredientRecipe),
     где есть ссылка на рецепт и ингредиент. В моделе Recipe, даю ссылку на таблицу Ingredient,
     через through='IngredientRecipe'. В IngredientRecipe появляется новый параметр amount, поэтому создаю эту 
     доп таблицу явно.
     Для тегов согласно не нужно доп таблицу, потому что там нет доп параметров.
     Чтобы при IngredientRecipe.objects.create(...) уже создаст нужную связь с рецептом.
     Если есть возможность на прямую связь с вами, можете дать ссылку на мессенджер или соц сеть, спасибо"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(null=True)

    class Meta:
        default_related_name = 'ingredients_recipes'
        verbose_name = 'Подсчет ингредиентов'
        verbose_name_plural = 'Подсчеты ингредиентов'

    def __str__(self):
        return f'{self.ingredient} {self.amount}'


class Favorite(models.Model):
    """Класс избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
        default_related_name = 'favorites'
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
    """Класс списка покупок рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, добавленный в список покупок '
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shop_recipe'
            )
        ]

        default_related_name = 'carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
