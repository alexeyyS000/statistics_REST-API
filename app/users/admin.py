from django.contrib import admin

from . import models


@admin.register(models.User)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MembershipLevel)
class ProfileAdmin(admin.ModelAdmin):
    fields = ["requests_number", "type"]
    list_display = ["type"]
    readonly_fields = ("type",)

    def has_add_permission(self, request):
        return False


@admin.register(models.Token)
class ProfileAdmin(admin.ModelAdmin):
    pass
