from django.db import models
from django.utils.html import format_html

from common.utils import DocumentTypeCategories, get_notification_category_image_upload_path
from jsonfield import JSONField


class Document(models.Model):
    type = models.CharField(max_length=30, choices=DocumentTypeCategories)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class BankDetail(models.Model):
    account_holder_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    bank_branch = models.CharField(max_length=300, blank=True, null=True)
    ifsc_code = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)


class AddressDetail(models.Model):
    street_address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    complete_address = models.TextField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.complete_address

    def save(self, *args, **kwargs):
        self.complete_address = "{}, {}, {}-{}".format(self.street_address, self.city, self.state, self.pincode)
        self.complete_address = self.complete_address.replace('None, ', '').replace('None-', '').replace('-None', '')
        super(AddressDetail, self).save(*args, **kwargs)

    @property
    def coordinates(self):
        return "{},{}".format(self.latitude, self.longitude)


class Wallet(models.Model):
    credit = models.FloatField(default=0)
    debit = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    pending_deposit = models.FloatField(default=0)
    pending_withdrawal = models.FloatField(default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        self.balance = round(self.credit - self.debit, 2)
        super(Wallet, self).save(*args, **kwargs)


class NotificationCategory(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(upload_to=get_notification_category_image_upload_path, null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_image = self.image
            self.image = None
            super(NotificationCategory, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(NotificationCategory, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    def get_notification_category_image_html(self):
        if self.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(self.image.url))
        else:
            return None

    get_notification_category_image_html.short_description = 'Notification Category Image'
    get_notification_category_image_html.allow_tags = True


class Notification(models.Model):
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    content = models.TextField(max_length=200, blank=True, null=True)
    payload = JSONField(blank=True, null=True)
    seen = models.BooleanField(default=False)
    display = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ('-timestamp',)

    def __str__(self):
        return str(self.id)
