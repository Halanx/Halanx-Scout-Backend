from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from UserBase.models import Customer
from chat.api.serializers import ConversationListSerializer, MessageSerializer
from chat.models import Conversation, Message, Participant
from chat.paginators import ChatPagination
from chat.utils import TYPE_CUSTOMER, TYPE_SCOUT
from scouts.models import Scout
from utility.rest_auth_utils import ChatParticipantAuthentication


def get_participant_from_request(request):
    try:
        if request.META['HTTP_PARTICIPANT_TYPE'] == TYPE_CUSTOMER:
            customer = Customer.objects.using(settings.HOMES_DB).get(user=request.user)
            participant, _ = Participant.objects.get_or_create(customer_id=customer.id, type=TYPE_CUSTOMER)
        elif request.META['HTTP_PARTICIPANT_TYPE'] == TYPE_SCOUT:
            scout = Scout.objects.get(user=request.user)
            participant, _ = Participant.objects.get_or_create(scout=scout, type=TYPE_SCOUT)
        else:
            raise ValidationError("No requesting participant found")

        return participant

    except ObjectDoesNotExist:
        raise Exception("no such {} exist".format(request.META['HTTP_PARTICIPANT_TYPE']))

    except MultipleObjectsReturned:
        raise Exception("multiple objects for {} returned".format(request.META['HTTP_PARTICIPANT_TYPE']))


class ConversationListView(ListAPIView):
    serializer_class = ConversationListSerializer
    authentication_classes = (ChatParticipantAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = ChatPagination

    def get_queryset(self):
        # will be used to pass in serializer context
        # noinspection PyAttributeOutsideInit
        self.requesting_participant = get_participant_from_request(self.request)

        return sorted(Conversation.objects.filter(participants=self.requesting_participant),
                      key=lambda t: t.last_message_timestamp,
                      reverse=True)

    def get_serializer_context(self):
        data = super(ConversationListView, self).get_serializer_context()
        data['requesting_participant'] = self.requesting_participant
        return data


class MessageListCreateView(ListCreateAPIView):
    serializer_class = MessageSerializer
    authentication_classes = (ChatParticipantAuthentication,)
    permission_classes = [IsAuthenticated, ]
    pagination_class = ChatPagination

    def create(self, request, *args, **kwargs):
        # will be used to pass in serializer context
        # noinspection PyAttributeOutsideInit
        self.requesting_participant = get_participant_from_request(self.request)

        conversation = Conversation.objects.get(id=self.kwargs.get('pk'), participants=self.requesting_participant)

        serializer = MessageSerializer(data=request.data, context=self.get_serializer_context())

        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=self.requesting_participant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # will be used to pass in serializer context
        # noinspection PyAttributeOutsideInit
        self.requesting_participant = get_participant_from_request(self.request)
        return Message.objects.filter(conversation__id=self.kwargs.get('pk'),
                                      conversation__participants=self.requesting_participant).order_by("-created_at")

    def get_serializer_context(self):
        data = super(MessageListCreateView, self).get_serializer_context()
        data['requesting_participant'] = self.requesting_participant
        return data
