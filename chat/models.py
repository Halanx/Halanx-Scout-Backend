from django.db import models

from chat.utils import ParticipantTypeCategories


class Participant(models.Model):
    type = models.CharField(max_length=10, choices=ParticipantTypeCategories)
    timestamp = models.DateTimeField(auto_now_add=True)


class Conversation(models.Model):
    participants = models.ManyToManyField(Participant)
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(Participant, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
