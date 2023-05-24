from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False, null=False,
    )
    email = models.EmailField(
        'Почта',
        max_length=254,
        unique=True,
        blank=False, null=False,
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False, null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False, null=False,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subsciber',
        verbose_name='Пользователь, который подписывается'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscibing',
        verbose_name='Пользователь, на которого подписываются'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
