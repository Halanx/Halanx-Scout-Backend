from rest_framework import serializers

from chat.models import Conversation, Message


class ConversationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = "__all__"


class MessageListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
