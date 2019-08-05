from django.contrib import admin

# Register your models here.
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup, PropertyOnBoardingHouseAddress, \
    PropertyOnBoardingHouseAmenity, PropertyOnBoardingHouseBasicDetail, PropertyOnBoardingHousePhoto, \
    PropertyOnBoardingPhoto, PropertyOnBoardingDetail
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


@admin.register(PropertyOnBoardingHouseAddress)
class PropertyOnBoardingHouseAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'location', 'latitude', 'longitude', 'street_address', 'city', 'state',)
    list_filter = (
        'city',
        'state',
        ('parent_subtask_category', admin.RelatedOnlyFieldListFilter),
        ('task__status', custom_titled_filter("Task Status")),
    )


@admin.register(PropertyOnBoardingHouseAmenity)
class PropertyOnBoardingHouseAmenityAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'amenities_json')
    list_filter = (
        ('parent_subtask_category', admin.RelatedOnlyFieldListFilter),
        ('task__status', custom_titled_filter("Task Status")),
    )


class PropertyOnBoardingPhotoInline(admin.TabularInline):
    model = PropertyOnBoardingPhoto


@admin.register(PropertyOnBoardingHousePhoto)
class PropertyOnBoardingHousePhotoAdmin(admin.ModelAdmin):
    inlines = (
        PropertyOnBoardingPhotoInline,
    )


@admin.register(PropertyOnBoardingHouseBasicDetail)
class PropertyOnBoardingHouseBasicDetailInline(admin.ModelAdmin):
    list_display = ('task', 'furnish_type', 'space_type', 'rent')
    list_filter = ('furnish_type', 'space_type')


@admin.register(PropertyOnBoardingDetail)
class PropertyOnBoardingDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_no', 'latitude', 'longitude', 'scheduled_at', 'location')