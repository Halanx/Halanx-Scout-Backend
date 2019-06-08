from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html

from common.models import AddressDetail, BankDetail, Wallet, Document
from common.utils import PaymentStatusCategories, PENDING, PAID
from scouts.utils import default_profile_pic_url, default_profile_pic_thumbnail_url, get_picture_upload_path, \
    get_thumbnail_upload_path, get_scout_document_upload_path, get_scout_document_thumbnail_upload_path
from utility.image_utils import compress_image


class Scout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='scout')
    phone_no = models.CharField(max_length=30, unique=True, validators=[RegexValidator('^[+]*\d{10,}$',
                                                                                       message="Phone Number should "
                                                                                               "contain at least 10 "
                                                                                               "numeric characters")])
    active = models.BooleanField(default=False)
    profile_pic_url = models.CharField(max_length=500, blank=True, null=True, default=default_profile_pic_url)
    profile_pic_thumbnail_url = models.CharField(max_length=500, blank=True, null=True,
                                                 default=default_profile_pic_thumbnail_url)

    def __str__(self):
        return str(self.id)

    @property
    def name(self):
        return self.user.get_full_name()

    def get_profile_pic_html(self):
        return format_html('<img src="{}" width="50" height="50" />'.format(self.profile_pic_url))

    get_profile_pic_html.short_description = 'Profile Pic'
    get_profile_pic_html.allow_tags = True
    
    
class ScoutPermanentAddress(AddressDetail):
    scout = models.OneToOneField('Scout', on_delete=models.CASCADE, related_name='permanent_address')

    
class ScoutWorkAddress(AddressDetail):
    scout = models.OneToOneField('Scout', on_delete=models.CASCADE, related_name='work_address')
    same_as_permanent_address = models.BooleanField(default=False)


class ScoutBankDetail(BankDetail):
    scout = models.OneToOneField('Scout', on_delete=models.CASCADE, related_name='bank_detail')


class ScoutWallet(Wallet):
    scout = models.OneToOneField('Scout', on_delete=models.PROTECT, related_name='wallet')


class ScoutPayment(models.Model):
    wallet = models.ForeignKey('ScoutWallet', on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.FloatField(default=0)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=30, default=PENDING, choices=PaymentStatusCategories)
    due_date = models.DateTimeField(blank=True, null=True)
    paid_on = models.DateTimeField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class ScoutPicture(models.Model):
    scout = models.ForeignKey('Scout', on_delete=models.SET_NULL, null=True, related_name='pictures')
    image = models.ImageField(upload_to=get_picture_upload_path, null=True, blank=True)
    thumbnail = models.ImageField(upload_to=get_thumbnail_upload_path, null=True, blank=True)
    is_profile_pic = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.pk:
            temp_name, output, thumbnail = compress_image(self.image, quality=90, _create_thumbnail=True)
            self.image.save(temp_name, content=ContentFile(output.getvalue()), save=False)
            self.thumbnail.save(temp_name, content=ContentFile(thumbnail.getvalue()), save=False)

        if self.is_deleted and self.is_profile_pic:
            self.is_profile_pic = False
            self.scout.profile_pic_url = default_profile_pic_url
            self.scout.profile_pic_thumbnail_url = default_profile_pic_thumbnail_url
            self.scout.save()
        super(ScoutPicture, self).save(*args, **kwargs)
        

class ScoutDocument(Document):
    scout = models.ForeignKey('Scout', null=True, on_delete=models.SET_NULL, related_name='documents')
    image = models.ImageField(upload_to=get_scout_document_upload_path, blank=True, null=True)
    thumbnail = models.ImageField(upload_to=get_scout_document_thumbnail_upload_path, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id is None:
            temp_name, output, thumbnail = compress_image(self.image, quality=90, _create_thumbnail=True)
            self.image.save(temp_name, content=ContentFile(output.getvalue()), save=False)
            self.thumbnail.save(temp_name, content=ContentFile(thumbnail.getvalue()), save=False)
        super(ScoutDocument, self).save(*args, **kwargs)        

        
class OTP(models.Model):
    phone_no = models.CharField(max_length=30)
    password = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class ScheduledAvailability(models.Model):
    scout = models.ForeignKey('Scout', on_delete=models.CASCADE, related_name='scheduled_availabilities')
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


# noinspection PyUnusedLocal
@receiver(post_save, sender=Scout)
def scout_post_save_hook(sender, instance, created, **kwargs):
    if created:
        ScoutPermanentAddress(scout=instance).save()
        ScoutWorkAddress(scout=instance).save()
        ScoutBankDetail(scout=instance).save()
        ScoutWallet(scout=instance).save()
        super(Scout, instance).save()


# noinspection PyUnusedLocal
@receiver(post_save, sender=ScoutPicture)
def scout_picture_post_save_task(sender, instance, *args, **kwargs):
    if instance.is_profile_pic:
        instance.scout.profile_pic_url = instance.image.url
        instance.scout.profile_pic_thumbnail_url = instance.thumbnail.url
        instance.scout.save()
        last_profile_pic = instance.scout.pictures.filter(is_profile_pic=True).exclude(id=instance.id).first()
        if last_profile_pic:
            last_profile_pic.is_profile_pic = False
            super(ScoutPicture, last_profile_pic).save()


# noinspection PyUnusedLocal
@receiver(post_save, sender=ScoutPayment)
def scout_payment_post_save_hook(sender, instance, created, **kwargs):
    wallet = instance.wallet
    wallet.debit = sum(payment.amount for payment in wallet.payments.filter(status=PAID))
    wallet.pending_withdrawal = sum(payment.amount for payment in wallet.payments.filter(status=PENDING))
    wallet.save()
