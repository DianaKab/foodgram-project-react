from django.contrib import admin
from users.models import Subscribe, User


class AdminUser(admin.ModelAdmin):
    """Класс администрирования модели User."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    search_fields = (
        'username',
        'email',
        'last_name',
    )

    list_filter = (
        'username',
        'email',
    )


admin.site.register(User, AdminUser)
admin.site.register(Subscribe)
