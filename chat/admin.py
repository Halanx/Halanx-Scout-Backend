from django.contrib import admin
from chat.models import Conversation, Message, Participant


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'conversation', 'sender')


class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'type')


admin.site.register(Conversation)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Message, MessageAdmin)
