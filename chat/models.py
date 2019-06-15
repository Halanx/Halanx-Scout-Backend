from django.conf import settings
from django.db import models

from UserBase.models import Customer
from chat.utils import ParticipantTypeCategories, TYPE_SCOUT, TYPE_CUSTOMER


class Participant(models.Model):
    type = models.CharField(max_length=30, choices=ParticipantTypeCategories)
    scout = models.OneToOneField('scouts.Scout', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='chat_participant')
    customer_id = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return "{}: {} ({})".format(self.id, self.name, self.type)

    @property
    def name(self):
        if self.type == TYPE_SCOUT:
            return self.scout.name
        elif self.type == TYPE_CUSTOMER:
            return Customer.objects.using(settings.HOMES_DB).get(id=self.customer_id).name


class Conversation(models.Model):
    task = models.OneToOneField('scouts.ScoutTask', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='conversation')
    participants = models.ManyToManyField('Participant', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    @property
    def last_message(self):
        return self.messages.last()

    @property
    def last_message_timestamp(self):
        last_message = self.last_message
        if last_message:
            return last_message.created_at.timestamp()
        else:
            return 0

    def other_participant(self, obj):
        """
        :param obj: requesting participant
        :return: other participant
        """
        return self.participants.exclude(id=obj.id)[0]


class Message(models.Model):
    conversation = models.ForeignKey('Conversation', on_delete=models.SET_NULL, related_name='messages', null=True)
    sender = models.ForeignKey('Participant', on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    receiver = models.ForeignKey('Participant', on_delete=models.SET_NULL, related_name='received_messages', null=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
