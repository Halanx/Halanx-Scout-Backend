from django.contrib import admin

# Register your models here.
from customers.models import CustomerNotificationCategory, CustomerNotification


@admin.register(CustomerNotificationCategory)
class CustomerNotificationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_notification_category_image_html')
    readonly_fields = ('get_notification_category_image_html',)


@admin.register(CustomerNotification)
class CustomerNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'category', 'content', 'get_notification_image_html',)
    search_fields = ('customer_id', )
    list_filter = ('category',)
