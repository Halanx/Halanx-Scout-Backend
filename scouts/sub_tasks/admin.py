from django.contrib import admin

# Register your models here.
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup


@admin.register(MoveOutRemark)
class MoveOutRemarkAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'task', 'parent_task_category', 'parent_subtask_category')
    list_filter = ('parent_task_category', 'parent_subtask_category', 'task__status')


@admin.register(MoveOutAmenitiesCheckup)
class AmenityCheckupModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'amenities_json', 'task', 'parent_task_category', 'parent_subtask_category')
    list_filter = ('parent_task_category', 'parent_subtask_category', 'task__status')