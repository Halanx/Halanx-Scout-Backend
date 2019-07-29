from django.db import models

# Create your models here.
from django.utils.html import format_html

from common.models import Notification, NotificationCategory
from .tasks import send_customer_notification


class CustomerNotificationCategory(NotificationCategory):
    class Meta:
        verbose_name_plural = 'Customer notification categories'


class CustomerNotification(Notification):
    customer_id = models.IntegerField()
    category = models.ForeignKey(CustomerNotificationCategory, on_delete=models.SET_NULL, null=True,
                                 related_name='notifications')

    def get_notification_image_html(self):
        if self.category and self.category.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(self.category.image.url))
        else:
            return None

    get_notification_image_html.short_description = 'Notification Image'
    get_notification_image_html.allow_tags = True

    def save(self, *args, **kwargs):
        if not self.pk:
            from customers.api.serializers import CustomerNotificationCategorySerializer
            send_customer_notification.delay(self.customer_id, title=self.category.name, content=self.content,
                                             category=CustomerNotificationCategorySerializer(self.category).data,
                                             payload=self.payload)
        super(CustomerNotification, self).save(*args, **kwargs)
