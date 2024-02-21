from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin
from django.contrib.auth.models import Group

from users.models import CustomUser


@admin.register(CustomUser)
class UserAdmin(BaseAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = (
        "username",
        "email",
    )


admin.site.unregister(Group)
