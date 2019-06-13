from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from UserBase.models import Customer
from chat.models import Conversation, Message, Participant
from scouts.models import Scout
from utility.timeutils import get_natural_datetime


# Scout APIs
class LastMessageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "content", "created_at"]

    @staticmethod
    def get_created_at(obj):
        return get_natural_datetime(obj.created_at)


class ScoutDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scout
        fields = ["id", "name", "profile_pic_url", "profile_pic_thumbnail_url"]


class ScoutConversationListSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "receiver", "task", "last_message"]

    def get_receiver(self, obj):
        customer_participant = obj.participants.exclude(id=self.context["scout_participant_id"])[0]
        try:
            return CustomerDetailSerializer(
                Customer.objects.using(settings.HOMES_DB).get(id=customer_participant.customer_id)).data
        except Customer.DoesNotExist:
            raise ValidationError({"detail": "No customer found in homes db"})

    @staticmethod
    def get_last_message(obj):
        return LastMessageSerializer(obj.messages.last()).data


class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "name", "profile_pic_url", "profile_pic_thumbnail_url"]


class MessageSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "content", "created_at"]

    @staticmethod
    def get_created_at(obj):
        return get_natural_datetime(obj.created_at)


class ScoutMessageListCreateSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'created_at', 'is_read', 'read_at', 'content', "sender"]

    def get_sender(self, obj):
        scout_participant_id = self.context["scout_participant_id"]
        print("id is", obj.sender.id)
        print(scout_participant_id)
        if obj.sender.id == scout_participant_id:
            return "self"
        else:
            customer_participant = obj.conversation.participants.exclude(id=self.context["scout_participant_id"])[0]
            return CustomerDetailSerializer(customer_participant).data


# Customer Serializers

class CustomerConversationListSerializer(serializers.ModelSerializer):
    receiver = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "receiver", "task", "last_message"]

    def get_receiver(self, obj):
        scout_participant = obj.participants.exclude(id=self.context["customer_participant_id"])[0]
        try:
            return ScoutDetailSerializer(scout_participant).data
        except Customer.DoesNotExist:
            raise ValidationError({"detail": "No Scout found in default db"})

    @staticmethod
    def get_last_message(obj):
        return LastMessageSerializer(obj.messages.last()).data


class ConversationMessageListCreateSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'created_at', 'is_read', 'read_at', 'content', "sender"]

    def get_sender(self, obj):
        customer_participant_id = self.context["customer_participant_id"]

        if obj.sender.id == customer_participant_id:  # if customer is a sender
            return "self"
        else:  # if customer is a receiver
            scout_participant = obj.conversation.participants.exclude(id=self.context["customer_participant_id"])[0]
            return ScoutDetailSerializer(scout_participant).data
