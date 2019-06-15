from django.contrib import admin
from chat.models import Conversation, Message, Participant


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'conversation', 'sender', 'receiver')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'customer_id', 'scout')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    pass
