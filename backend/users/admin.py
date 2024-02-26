from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from users.models import CustomUser, Subscription


@admin.register(CustomUser)
class UserAdmin(UserAdmin):
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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
    search_fields = ("user",)


admin.site.unregister(Group)
