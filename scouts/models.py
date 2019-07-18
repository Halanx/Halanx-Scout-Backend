import random
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.signals import user_logged_out
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.html import format_html

from Homes.Bookings.models import Booking
from Homes.Houses.models import HouseVisit
from chat.models import Conversation, Participant
from chat.utils import TYPE_SCOUT, TYPE_CUSTOMER
from common.models import AddressDetail, BankDetail, Wallet, Document, NotificationCategory, Notification
from common.utils import PaymentStatusCategories, PENDING, PAID, DocumentTypeCategories, WITHDRAWAL, \
    PaymentTypeCategories, DEPOSIT
from scouts.tasks import send_scout_notification, scout_assignment_request_set_rejected
from scouts.utils import default_profile_pic_url, default_profile_pic_thumbnail_url, get_picture_upload_path, \
    get_thumbnail_upload_path, get_scout_document_upload_path, get_scout_document_thumbnail_upload_path, \
    get_scout_task_category_image_upload_path, ScoutTaskStatusCategories, \
    ScoutTaskAssignmentRequestStatusCategories, REQUEST_AWAITED, NEW_TASK_NOTIFICATION, REQUEST_ACCEPTED, \
    REQUEST_REJECTED, ASSIGNED, get_appropriate_scout_for_the_house_visit_task, COMPLETE, NEW_PAYMENT_RECEIVED, \
    get_description_for_completion_of_current_task_and_receiving_payment_in_wallet, \
    get_description_for_completion_of_current_task_and_receiving_payment_in_bank_account
from utility.image_utils import compress_image
from utility.logging_utils import sentry_debug_logger


class Flag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    enabled = models.BooleanField(default=True)


class Scout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='scout')
    phone_no = models.CharField(max_length=30, unique=True, validators=[RegexValidator('^[+]*\d{10,}$',
                                                                                       message="Phone Number should "
                                                                                               "contain at least 10 "
                                                                                               "numeric characters")])
    active = models.BooleanField(default=False)
    profile_pic_url = models.CharField(max_length=500, blank=True, null=True, default=default_profile_pic_url)
    profile_pic_thumbnail_url = models.CharField(max_length=500, blank=True, null=True,
                                                 default=default_profile_pic_thumbnail_url)

    gcm_id = models.CharField(max_length=500, blank=True, null=True)
    rating = models.FloatField(default=0)
    review_tags = models.ManyToManyField('ScoutTaskReviewTagCategory', blank=True, related_name='scouts')
    priority = models.IntegerField(default=0)

    def __str__(self):
        return "{}:{}".format(self.id, self.phone_no)

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def latest_documents(self):
        documents = self.documents.filter(is_deleted=False).order_by('-id')
        latest_documents = []
        for doc_type in list(zip(*DocumentTypeCategories))[0]:
            latest_documents.extend(documents.filter(type=doc_type)[:2])
        return list(filter(lambda x: x is not None, latest_documents))

    @property
    def document_submission_complete(self):
        documents = self.documents.filter(is_deleted=False)
        counts = []
        for doc_type in list(zip(*DocumentTypeCategories))[0]:
            counts.append(documents.filter(type=doc_type).count())
        return all(counts)

    @property
    def bank_details_complete(self):
        bank_detail = self.bank_detail
        return all([bank_detail.account_holder_name, bank_detail.account_number, bank_detail.bank_name])

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
    type = models.CharField(max_length=30, default=WITHDRAWAL, choices=PaymentTypeCategories)
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
            self.image = None
            self.thumbnail = None
            super(ScoutDocument, self).save(*args, **kwargs)
            self.image.save(temp_name, content=ContentFile(output.getvalue()), save=False)
            self.thumbnail.save(temp_name, content=ContentFile(thumbnail.getvalue()), save=False)
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')

        super(ScoutDocument, self).save(*args, **kwargs)


class OTP(models.Model):
    phone_no = models.CharField(max_length=30)
    password = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class ScoutNotificationCategory(NotificationCategory):
    class Meta:
        verbose_name_plural = 'Scout notification categories'


class ScoutNotification(Notification):
    scout = models.ForeignKey('Scout', on_delete=models.CASCADE, related_name='notifications')
    category = models.ForeignKey('ScoutNotificationCategory', on_delete=models.SET_NULL, null=True,
                                 related_name='notifications')

    def save(self, *args, **kwargs):
        if not self.pk:
            from scouts.api.serializers import ScoutTaskCategorySerializer
            send_scout_notification.delay(self.scout.id, title=self.category.name, content=self.content,
                                          category=ScoutTaskCategorySerializer(self.category).data,
                                          payload=self.payload)
        super(ScoutNotification, self).save(*args, **kwargs)

    def get_notification_image_html(self):
        if self.category and self.category.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(self.category.image.url))
        else:
            return None

    get_notification_image_html.short_description = 'Notification Image'
    get_notification_image_html.allow_tags = True


class ScheduledAvailability(models.Model):
    scout = models.ForeignKey('Scout', on_delete=models.CASCADE, related_name='scheduled_availabilities')
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class ScoutTaskCategory(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_scout_task_category_image_upload_path, null=True, blank=True)
    earning = models.FloatField(default=0)

    class Meta:
        verbose_name_plural = 'Scout task categories'

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if self.id is None:
            saved_image = self.image
            self.image = None
            super(ScoutTaskCategory, self).save(*args, **kwargs)
            self.image = saved_image
            if 'force_insert' in kwargs:
                kwargs.pop('force_insert')
        super(ScoutTaskCategory, self).save(*args, **kwargs)

    def get_scout_task_category_image_html(self):
        if self.image:
            return format_html('<img src="{}" width="50" height="50" />'.format(self.image.url))
        else:
            return None

    get_scout_task_category_image_html.short_description = 'category Image'
    get_scout_task_category_image_html.allow_tags = True


class ScoutSubTaskCategory(models.Model):
    name = models.CharField(max_length=255)
    task_category = models.ForeignKey('ScoutTaskCategory', on_delete=models.SET_NULL, null=True,
                                      related_name='sub_task_categories')
    position = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name_plural = 'Scout sub task categories'
        ordering = ('position',)

    def __str__(self):
        return str(self.name)


class ScoutTaskReviewTagCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Scout task review status categories'

    def __str__(self):
        return str(self.name)


class ScoutTask(models.Model):
    scout = models.ForeignKey('Scout', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    category = models.ForeignKey('ScoutTaskCategory', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='tasks')
    sub_tasks = models.ManyToManyField('ScoutSubTaskCategory', blank=True)
    status = models.CharField(max_length=50, choices=ScoutTaskStatusCategories)
    earning = models.FloatField(default=0)

    house_id = models.PositiveIntegerField(blank=True, null=True)
    visit_id = models.PositiveIntegerField(blank=True, null=True)
    booking_id = models.PositiveIntegerField(blank=True, null=True)

    scheduled_at = models.DateTimeField(blank=True, null=True)
    assigned_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    rating = models.PositiveIntegerField(default=0)
    rating_given = models.BooleanField(default=False)

    remark = models.TextField(blank=True, null=True)
    review_tags = models.ManyToManyField('ScoutTaskReviewTagCategory', blank=True, related_name='tasks')
    payment = models.ForeignKey('ScoutPayment', on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    def __str__(self):
        return str(self.id)

    @property
    def visit(self):
        if self.visit_id:
            return (HouseVisit.objects.using(settings.HOMES_DB).select_related('customer')
                .filter(id=self.visit_id).first())

    @property
    def booking(self):
        if self.booking_id:
            return (Booking.objects.using(settings.HOMES_DB).select_related('tenant__customer')
                .filter(id=self.booking_id).first())

    @property
    def customer(self):
        if self.visit_id:
            visit = self.visit
            if self.visit:
                return visit.customer
        if self.booking_id:
            booking = self.booking
            if booking and booking.tenant:
                return booking.tenant.customer


class ScoutTaskAssignmentRequest(models.Model):
    task = models.ForeignKey('ScoutTask', on_delete=models.SET_NULL, null=True, related_name='assignment_requests')
    scout = models.ForeignKey('Scout', on_delete=models.SET_NULL, null=True, related_name='task_assignment_requests')
    status = models.CharField(max_length=50, choices=ScoutTaskAssignmentRequestStatusCategories,
                              default=REQUEST_AWAITED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(blank=True, null=True)

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
        Participant(scout=instance, type=TYPE_SCOUT).save()
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
@receiver(pre_save, sender=ScoutPayment)
def scout_payment_pre_save_hook(sender, instance, **kwargs):
    old_payment = ScoutPayment.objects.filter(id=instance.id).first()
    if not old_payment:
        return

    if old_payment.status == PENDING and instance.status == PAID:
        instance.paid_on = datetime.now()
        from scouts.api.serializers import ScoutPaymentSerializer

        if instance.type == WITHDRAWAL:
            new_payment_received_notification_category, _ = ScoutNotificationCategory.objects. \
                get_or_create(name=NEW_PAYMENT_RECEIVED)

            ScoutNotification.objects.create(category=new_payment_received_notification_category,
                                             scout=instance.wallet.scout,
                                             payload=ScoutPaymentSerializer(instance).data, display=True)


@receiver(post_save, sender=ScoutPayment)
def scout_payment_post_save_hook(sender, instance, created, **kwargs):
    wallet = instance.wallet
    wallet.debit = sum(payment.amount for payment in wallet.payments.filter(type=WITHDRAWAL, status=PAID))
    wallet.credit = sum(payment.amount for payment in wallet.payments.filter(type=DEPOSIT, status=PAID))
    wallet.pending_deposit = sum(payment.amount for payment in wallet.payments.filter(type=DEPOSIT, status=PENDING))
    wallet.pending_withdrawal = sum(payment.amount for payment in wallet.payments.filter(type=WITHDRAWAL,
                                                                                         status=PENDING))
    wallet.save()


@receiver(pre_save, sender=ScoutTask)
def scout_task_pre_save_hook(sender, instance, **kwargs):
    old_task = ScoutTask.objects.filter(id=instance.id).first()
    if not old_task:
        return

    old_scout = old_task.scout
    new_scout = instance.scout

    # Manage Conversation
    conversation = instance.conversation

    if conversation:
        if old_scout != new_scout:
            if old_scout and old_scout.chat_participant in conversation.participants.all():
                conversation.participants.remove(old_scout.chat_participant)
                conversation.save()

            if new_scout and new_scout.chat_participant not in conversation.participants.all():
                conversation.participants.add(new_scout.chat_participant)
                conversation.save()

    if old_task.status == ASSIGNED and instance.status == COMPLETE:
        instance.completed_at = datetime.now()

        # 1 Create a payment that shows amount to be deposited in the wallet by the company
        ScoutPayment.objects.create(
            wallet=instance.scout.wallet,
            amount=instance.category.earning,
            description=get_description_for_completion_of_current_task_and_receiving_payment_in_wallet(instance),
            type=DEPOSIT, status=PENDING)

        # 2 Create a payment that shows amount to be withdrawn from the wallet by the user
        ScoutPayment.objects.create(
            wallet=instance.scout.wallet, amount=instance.category.earning,
            description=get_description_for_completion_of_current_task_and_receiving_payment_in_bank_account(instance),
            type=WITHDRAWAL, status=PENDING)

        # Note: Both the above payments are to be verified by company by changing the status to paid

    # Manage rating given to Scout
    if not old_task.rating_given and instance.rating_given:
        scout = instance.scout
        previous_ratings = ScoutTask.objects.filter(scout=scout)
        scout.rating = (previous_ratings.aggregate(Sum('rating'))['rating__sum'] + instance.rating) / (len(previous_ratings) + 1)
        scout.save()


# noinspection PyUnusedLocal
@receiver(post_save, sender=ScoutTask)
def scout_task_post_save_hook(sender, instance, created, **kwargs):
    if created:
        conversation, created = Conversation.objects.get_or_create(task=instance)
        customer = instance.customer
        if customer:
            customer_participant, created = Participant.objects.get_or_create(customer_id=customer.id,
                                                                              type=TYPE_CUSTOMER)

            if customer_participant not in conversation.participants.all():
                conversation.participants.add(customer_participant)


# noinspection PyUnusedLocal
@receiver(post_save, sender=ScoutTaskAssignmentRequest)
def scout_task_assignment_request_post_save_hook(sender, instance, created, **kwargs):
    # just sending the notification
    task = instance.task
    if created and task:
        new_task_notification_category, _ = ScoutNotificationCategory.objects.get_or_create(name=NEW_TASK_NOTIFICATION)
        from scouts.api.serializers import NewScoutTaskNotificationSerializer
        ScoutNotification.objects.create(category=new_task_notification_category, scout=instance.scout,
                                         payload=NewScoutTaskNotificationSerializer(task).data, display=False)

        try:
            send_date = timezone.now() + timedelta(minutes=2)
            scout_assignment_request_set_rejected.apply_async([instance.id], eta=send_date)
            sentry_debug_logger.debug('auto rejecting after 2 minutes', exc_info=True)
        except Exception as E:
            sentry_debug_logger.error('error is ' + str(E), exc_info=True)


# noinspection PyUnusedLocal
@receiver(pre_save, sender=ScoutTaskAssignmentRequest)
def scout_task_assignment_request_pre_save_hook(sender, instance, update_fields={'responded_at'}, **kwargs):
    old_request = ScoutTaskAssignmentRequest.objects.filter(id=instance.id).first()
    if not old_request:
        return

    if old_request.status == REQUEST_AWAITED and instance.status in [REQUEST_ACCEPTED, REQUEST_REJECTED]:
        instance.responded_at = timezone.now()
        task = instance.task
        if instance.status == REQUEST_ACCEPTED:
            task.scout = instance.scout
            task.status = ASSIGNED
            task.assigned_at = instance.responded_at
            task.save()

        elif instance.status == REQUEST_REJECTED:
            # find some other scout to send notification to
            # create another scout task assignment request
            sentry_debug_logger.debug('scout rejected the request')

            # find another scout for the visit task excluding this scout
            scout = get_appropriate_scout_for_the_house_visit_task(task=task,
                                                                   scouts=Scout.objects.filter(active=True).exclude(
                                                                       id=instance.scout.id))

            if scout:
                ScoutTaskAssignmentRequest.objects.create(task=task, scout=scout)

            else:
                sentry_debug_logger.debug("no more scout exists")


# noinspection PyUnusedLocal
@receiver(post_save, sender=ScoutWorkAddress)
def scout_work_address_save_task(sender, instance, created, **kwargs):
    if created:
        if instance.latitude is None:
            instance.latitude = random.uniform(28.4595, 28.5355)  # random latitude in Delhi

        if instance.longitude is None:
            instance.longitude = random.uniform(77.0266, 77.3910)  # random longitude in Delhi

        print("created")
        instance.save()


@receiver(user_logged_out)
def user_logged_out(sender, user, **kwargs):
    try:
        scout = user.scout
        scout.active = False
        scout.save()
    except Exception as E:
        sentry_debug_logger.debug('no scout found' + str(E), exc_info=True)
