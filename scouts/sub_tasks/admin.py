from django.contrib import admin

# Register your models here.
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup
from utility.admin_site_utils import custom_titled_filter


@admin.register(MoveOutRemark)
class MoveOutRemarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'task', 'parent_task_category', 'parent_subtask_category')
    list_filter = (
        ('parent_subtask_category', admin.RelatedOnlyFieldListFilter),
        ('task__status', custom_titled_filter("Task Status")),
    )


@admin.register(MoveOutAmenitiesCheckup)
class AmenityCheckupModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'amenities_json', 'task', 'parent_subtask_category')
    list_filter = (
        ('parent_subtask_category', admin.RelatedOnlyFieldListFilter),
        ('task__status', custom_titled_filter("Task Status")),
    )
