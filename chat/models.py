from django.conf import settings
from django.db import models

from UserBase.models import Customer
from chat.utils import ParticipantTypeCategories, TYPE_SCOUT, TYPE_TENANT


class Participant(models.Model):
    type = models.CharField(max_length=30, choices=ParticipantTypeCategories)
    scout = models.OneToOneField("scouts.Scout", on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="participant")
    customer_id = models.PositiveIntegerField(null=True, blank=True)  # used for tenant

    def __str__(self):
        return str(self.id) + "(" + str(self.type) + ")"

    @property
    def name(self):
        if self.type == TYPE_SCOUT:
            return str(self.scout.name)
        elif self.type == TYPE_TENANT:
            return Customer.objects.using(settings.HOMES_DB).get(id=self.customer_id).tenant.name


class Conversation(models.Model):
    task = models.OneToOneField("scouts.ScoutTask", on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="conversation")
    participants = models.ManyToManyField(Participant, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, related_name="messages", null=True, blank=True)
    sender = models.ForeignKey(Participant, on_delete=models.SET_NULL, related_name="messages", null=True, blank=True)
    content = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)
