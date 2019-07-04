from decouple import config
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from UserBase.models import Customer
from chat.api.serializers import ConversationListSerializer, MessageSerializer
from chat.models import Conversation, Message, Participant, SocketClient
from chat.paginators import ChatPagination
from chat.utils import TYPE_CUSTOMER, TYPE_SCOUT, SOCKET_STATUS_CONNECTED, SOCKET_STATUS_DISCONNECTED, \
    NODE_SERVER_CHAT_ENDPOINT
from scouts.models import Scout
from utility.rest_auth_utils import ChatParticipantAuthentication
from rest_framework.decorators import api_view, authentication_classes
from django.http import JsonResponse
import requests


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


def send_message_to_receiver_participant_via_socket(data, receiver_participant):
    try:
        request_data = {'data': data, 'receiver_socket_id': receiver_participant.socket_clients.first().socket_id,
                        'server_password': config('NODEJS_SERVER_PASSWORD')}
        x = requests.post(NODE_SERVER_CHAT_ENDPOINT, data=request_data)
        print(x.content)
        return x.status_code
    except Exception as E:
        print("message not sent due to", E)
        return None


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
            msg = serializer.save(conversation=conversation, sender=self.requesting_participant,
                                  receiver=conversation.other_participant(self.requesting_participant))

            # Sending Message to Node JS Socket Server via post request
            send_message_to_receiver_participant_via_socket(
                data=MessageSerializer(msg, context=self.get_serializer_context()).data,
                receiver_participant=msg.receiver)

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


@api_view(('POST',))
@authentication_classes((ChatParticipantAuthentication,))
def get_socket_id_from_node_server(request):
    result = {}
    try:
        requesting_participant = get_participant_from_request(request)
        socket_id = request.data['socket_id']
        data = request.data['data']
        # user = request.auth.user

        # Adding Socket to Socket Client
        if data['socket_status'] == SOCKET_STATUS_CONNECTED:
            socket_client, created = SocketClient.objects.update_or_create(
                defaults={'socket_id': socket_id,
                          'participant': requesting_participant
                          },
                participant=requesting_participant)

            result = {'status': 'success', 'socket_id': socket_client.socket_id, 'message': "connected succesfully"}

        # Remove Socket from Socket Table
        elif data['socket_status'] == SOCKET_STATUS_DISCONNECTED:
            deleted, _ = SocketClient.objects.filter(socket_id=socket_id, participant=requesting_participant).delete()
            if deleted:
                result = {'status': 'success', 'socket_id': socket_id, 'message': 'disconnected succesfully'}
            else:
                result = {'status': 'error', 'message': 'No Such Client Exists'}

    except Exception as E:
        print(E)
        result = {'status': 'error', 'message': str(E)}

    return JsonResponse(result)
