from django.db import models

from chat.utils import ParticipantTypeCategories


class Participant(models.Model):
    type = models.CharField(max_length=30, choices=ParticipantTypeCategories)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + "(" + str(self.type) + ")"


class Conversation(models.Model):
    participants = models.ManyToManyField(Participant)
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(Participant, on_delete=models.CASCADE)
    content = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
