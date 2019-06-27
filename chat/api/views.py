from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from UserBase.models import Customer
from chat.models import Conversation, Message, Participant
from chat.paginators import ConversationPagination
from utility.rest_auth_utils import ChatParticipantAuthentication, TYPE_CUSTOMER_PARTICIPANT, \
    TYPE_SCOUT_PARTICIPANT
from .serializers import GenericConversationListSerializer, \
    GenericMessageListCreateSerializer


def get_participant_from_request(request):
    try:
        if request.META["HTTP_PARTICIPANT_TYPE"] == TYPE_CUSTOMER_PARTICIPANT:
            customer = Customer.objects.using(settings.HOMES_DB).get(user=request.user)
            participant = Participant.objects.get(customer_id=customer.id)
        elif request.META["HTTP_PARTICIPANT_TYPE"] == TYPE_SCOUT_PARTICIPANT:
            participant = Participant.objects.get(scout__user=request.user)
        else:
            raise ValidationError({"detail": "No requesting participant found"})

        return participant

    except ObjectDoesNotExist:
        raise Exception("no such {} does not exist".format(request.META["HTTP_PARTICIPANT_TYPE"]))

    except MultipleObjectsReturned:
        raise Exception("multiple objects for {} returned".format(request.META["HTTP_PARTICIPANT_TYPE"]))


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
@authentication_classes((ChatParticipantAuthentication,))
def get_logged_in_user(request):
    print(request.META)
    return HttpResponse(str(request.user))


# Generic Conversations
class GenericConversationListView(ListAPIView):
    serializer_class = GenericConversationListSerializer
    authentication_classes = (ChatParticipantAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = ConversationPagination

    def get_queryset(self):
        # will be used to pass in serializer context
        self.requesting_participant = get_participant_from_request(self.request)

        return sorted(Conversation.objects.filter(
            participants=self.requesting_participant),
            key=lambda t: t.last_message_time, reverse=True)

    def get_serializer_context(self):
        data = super(GenericConversationListView, self).get_serializer_context()
        data["requesting_participant"] = self.requesting_participant.id
        return data


class GenericMessageListCreateView(ListCreateAPIView):
    serializer_class = GenericMessageListCreateSerializer
    authentication_classes = (ChatParticipantAuthentication,)
    permission_classes = [IsAuthenticated, ]
    pagination_class = ConversationPagination

    def create(self, request, *args, **kwargs):
        # will be used to pass in serializer context
        self.requesting_participant = get_participant_from_request(self.request)

        conversation = Conversation.objects.get(id=self.kwargs.get('pk'),
                                                participants=self.requesting_participant)

        serializer = GenericMessageListCreateSerializer(data=request.data, context=self.get_serializer_context())
        if serializer.is_valid():
            serializer.save(conversation=conversation, sender=self.requesting_participant,
                            receiver=conversation.other_participant(self.requesting_participant.id))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # will be used to pass in serializer context
        self.requesting_participant = get_participant_from_request(self.request)
        return Message.objects.filter(conversation__id=self.kwargs.get('pk'),
                                      conversation__participants=self.requesting_participant).order_by("-created_at")

    def get_serializer_context(self):
        data = super(GenericMessageListCreateView, self).get_serializer_context()
        data["requesting_participant"] = self.requesting_participant.id
        return data
