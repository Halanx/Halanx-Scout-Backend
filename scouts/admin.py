from django.contrib import admin

from scouts.models import Scout


@admin.register(Scout)
class ScoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone_no', )
