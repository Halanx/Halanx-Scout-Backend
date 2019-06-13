from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chat.models import Conversation, Message, Participant
from .serializers import ConversationListSerializer, MessageListCreateSerializer


def get_participant_from_request(request):
    if not request.user.is_anonymous:
        p, created = Participant.objects.get_or_create(user=request.user)
        return p
    else:
        raise ValidationError("Authenticated request only")


@api_view(("GET",))
@permission_classes((IsAuthenticated,))
def get_logged_in_user(request):
    return HttpResponse(str(request.user))


class ConversationListAPIView(ListAPIView):
    """It displays the list of conversations of logged in user"""
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Conversation.objects.filter(participants__id__in=[get_participant_from_request(self.request).id])


class MessageListCreateAPIView(ListCreateAPIView):
    """It displays the list of messages of logged in user of given conversation"""
    serializer_class = MessageListCreateSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data["sender"] = get_participant_from_request(request).id
        try:
            request.data["conversation"] = Conversation.objects.get(id=self.kwargs.get('pk'),
                                                                    participants__id__in=[request.data["sender"], ]).pk

        except Conversation.DoesNotExist:
            raise ValidationError({"detail": "No such Conversation Exists"})

        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Message.objects.filter(conversation__id=self.kwargs.get('pk'),
                                      conversation__participants=get_participant_from_request(self.request))
