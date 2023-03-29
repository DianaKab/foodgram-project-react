from colorfield.fields import ColorField
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    amount = models.IntegerField(blank=True, null=True)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        )
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='recipes/', null=False, blank=False)
    text = models.TextField()
    # ingredients = models.ForeignKey(
    #     Ingredient,
    #     blank=False,
    #     null=False,
    #     on_delete=models.CASCADE,
    #     related_name='recipes',
    #     verbose_name='Ингредиенты',
    #     help_text='Описание'
    # )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe'
    )
    cooking_time = models.IntegerField()
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        default_related_name = 'recipes'
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['user', 'recipe'],
        #         name='unique_user_recipe'
        #     )
        # ]
        default_related_name = 'favorites'
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'


class ShoppingCart(models.Model):
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
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['user', 'shop_recipe'],
        #         name='unique_user_shop_recipe'
        #     )
        # ]

        default_related_name = 'shoppings'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
