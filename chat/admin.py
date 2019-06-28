from django.contrib import admin
from chat.models import Conversation, Message, Participant, SocketClient


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'conversation', 'sender', 'receiver')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'customer_id', 'scout')


@admin.register(Conversation)
class ConversationModelAdmin(admin.ModelAdmin):
    pass


@admin.register(SocketClient)
class SocketClientModelAdmin(admin.ModelAdmin):
    list_display = ('socket_id', 'participant')
