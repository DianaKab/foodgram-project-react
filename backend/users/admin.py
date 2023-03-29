from django.contrib import admin
from users.models import User


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


admin.site.register(User, AdminUser)
