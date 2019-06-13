from django.conf import settings
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from UserBase.models import Customer
from chat.models import Conversation, Message, Participant
from chat.paginators import ConversationPagination
from .serializers import ScoutConversationListSerializer, ScoutMessageListCreateSerializer,\
    CustomerConversationListSerializer, ConversationMessageListCreateSerializer


def get_scout_participant_from_request(request):
    try:
        p = Participant.objects.get(scout__user=request.user)
    except Participant.DoesNotExist:
        raise ValidationError({"detail": "Participant: Does not exist"})
    except Participant.MultipleObjectsReturned:
        raise ValidationError({"detail": "Participant: multiple objects returned"})
    return p


def get_customer_participant_from_request(request):
    try:
        customer = Customer.objects.using(settings.HOMES_DB).get(user=request.user)
    except Customer.DoesNotExist:
        raise ValidationError({"detail": "Customer: does not exist"})
    except Customer.MultipleObjectsReturned:
        raise ValidationError({"detail": "Customer: multiple objects returned"})

    try:
        p = Participant.objects.get(customer=customer)
    except Participant.DoesNotEXist:
        raise ValidationError({"detail": "Participant:  does not exist"})
    except Participant.MultipleObjectsReturned:
        raise ValidationError({"detail": "Participant: multiple objects returned"})
    return p


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def get_logged_in_user(request):
    return HttpResponse(str(request.user))


# Scouts Conversations

class ScoutConversationListAPIView(ListAPIView):
    """It displays the list of conversations of logged in scout"""
    serializer_class = ScoutConversationListSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = ConversationPagination

    def get_queryset(self):
        scout_participant = get_scout_participant_from_request(self.request)

        # Adding Scout Participant to pass in serializer context
        self.scout_participant = scout_participant
        return sorted(Conversation.objects.filter(
            participants=scout_participant),
            key=lambda t: t.last_message_time, reverse=True)

    def get_serializer_context(self):
        data = super(ScoutConversationListAPIView, self).get_serializer_context()
        data["scout_participant_id"] = self.scout_participant.id
        return data


class ScoutMessageListCreateAPIView(ListCreateAPIView):
    """It displays the list of messages of logged in scout of given conversation"""
    serializer_class = ScoutMessageListCreateSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = ConversationPagination

    def create(self, request, *args, **kwargs):
        sender_scout = get_scout_participant_from_request(self.request)
        # Adding Scout Participant to pass in serializer context
        self.scout_participant = sender_scout

        conversation = Conversation.objects.get(id=self.kwargs.get('pk'),
                                                participants=sender_scout)

        serializer = ScoutMessageListCreateSerializer(request.data)

        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=sender_scout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        sender_scout = get_scout_participant_from_request(self.request)
        # Adding Scout Participant to pass in serializer context
        self.scout_participant = sender_scout
        return Message.objects.filter(conversation__id=self.kwargs.get('pk'),
                                      conversation__participants=get_scout_participant_from_request(
                                          self.request)).order_by("-created_at")

    def get_serializer_context(self):
        data = super(ScoutMessageListCreateAPIView, self).get_serializer_context()
        data["scout_participant_id"] = self.scout_participant.id
        return data


# Customer Conversations

class CustomerConversationListAPIView(ListAPIView):
    """It displays the list of conversations of logged in customer"""
    serializer_class = CustomerConversationListSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = ConversationPagination

    def get_queryset(self):
        customer_participant = get_customer_participant_from_request(self.request)

        # Adding customer Participant to pass in serializer context
        self.customer_participant = customer_participant
        return sorted(Conversation.objects.filter(
            participants=customer_participant),
            key=lambda t: t.last_message_time, reverse=True)

    def get_serializer_context(self):
        data = super(CustomerConversationListAPIView, self).get_serializer_context()
        data["customer_participant_id"] = self.customer_participant.id
        return data


class CustomerMessageListCreateAPIView(ListCreateAPIView):
    """It displays the list of messages of logged in customer of given conversation"""
    serializer_class = ConversationMessageListCreateSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = ConversationPagination

    def create(self, request, *args, **kwargs):
        customer_participant = get_customer_participant_from_request(self.request)
        # Adding customer Participant to pass in serializer context
        self.customer_participant = customer_participant

        conversation = Conversation.objects.get(id=self.kwargs.get('pk'),
                                                participants=customer_participant)

        serializer = ConversationMessageListCreateSerializer(request.data)

        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=customer_participant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        customer_partcipant = get_customer_participant_from_request(self.request)
        # Adding Scout Participant to pass in serializer context
        self.customer_participant = customer_partcipant
        return Message.objects.filter(conversation__id=self.kwargs.get('pk'),
                                      conversation__participants=customer_partcipant).order_by("-created_at")

    def get_serializer_context(self):
        data = super(CustomerMessageListCreateAPIView, self).get_serializer_context()
        data["customer_participant_id"] = self.customer_participant.id
        return data


