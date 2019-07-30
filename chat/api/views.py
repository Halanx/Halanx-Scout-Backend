import json
from copy import deepcopy

import requests
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
from chat.models import Conversation, Message, Participant
from chat.paginators import ChatPagination
from chat.utils import TYPE_CUSTOMER, TYPE_SCOUT, NODE_SERVER_CHAT_ENDPOINT, \
    SCOUT_CUSTOMER_SOCKET_CHAT_CONVERSATION_PREFIX
from customers.models import CustomerNotification, CustomerNotificationCategory
from customers.utils import NEW_SCOUT_MESSAGE_NC
from scouts.models import Scout, ScoutTask, ScoutNotification, ScoutNotificationCategory
from scouts.utils import NEW_MESSAGE_RECEIVED
from utility.environments import PRODUCTION
from utility.logging_utils import sentry_debug_logger
from utility.redis_utils import ConsumerAppRedis
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
        queryset = Conversation.objects.filter(participants=self.requesting_participant)

        if self.requesting_participant.type == TYPE_CUSTOMER:
            if 'task_id' in self.request.GET:
                # TODO verify that task belongs to the customer only
                task = ScoutTask.objects.filter(id=self.request.GET['task_id']).first()
                if task and task.conversation:
                    queryset = queryset.filter(participants=task.scout.chat_participant)

        return sorted(queryset,
                      key=lambda t: t.last_message_timestamp,
                      reverse=True)

    def get_serializer_context(self):
        data = super(ConversationListView, self).get_serializer_context()
        data['requesting_participant'] = self.requesting_participant
        return data


def send_message_to_receiver_participant_via_consumer_app(msg, data, receiver_participant):
    """
    In this chat when Scout is sending a message we publish message with sender as scout id and receiver as
    receiving customer id. and if Scout is receiving a message then we publish message with sender as customer_id
    and receiver as scout id
    For more reference see Halanx-node/index.js AND
    Halanx-db/Chat/api/views.py - scout_chat_view
    SCOUT_CUSTOMER_SOCKET_CHAT_CONVERSATION_PREFIX used for conversation between scout and customer

    # TODO: The chat may fail when scout chats with customer when scout_id = customer_id because that will lead to
    # TODO: same key for redis i.e for e.g  SCOUTCHAT:5 = SCOUTCHAT:5
    """
    data_copy = deepcopy(data)

    if receiver_participant.type == TYPE_SCOUT:
        scout = receiver_participant.scout
        scout_id = scout.id
        data['sender'] = msg.sender.customer_id
        data['receiver'] = SCOUT_CUSTOMER_SOCKET_CHAT_CONVERSATION_PREFIX + str(scout_id)

    elif receiver_participant.type == TYPE_CUSTOMER:
        customer_id = receiver_participant.customer_id
        data['sender'] = msg.sender.scout.id
        data['receiver'] = SCOUT_CUSTOMER_SOCKET_CHAT_CONVERSATION_PREFIX + str(customer_id)

    # Send Message if Online
    if settings.ENVIRONMENT == PRODUCTION:
        r = ConsumerAppRedis()

        if r.get(data['receiver']):  # Receiver is Online
            sentry_debug_logger.debug("user is online")
            data['message_data'] = data_copy
            # In case of socket the role will always be receiver
            data['message_data']['role'] = 'receiver'
            scout_chat_receiver_id = data['receiver']

            if r.get(scout_chat_receiver_id):
                msg = json.dumps(data)
                r.publish('onChat', msg)

        else:
            sentry_debug_logger.debug('user is offline')

            if receiver_participant.type == TYPE_SCOUT:
                new_message_received_notification_category, _ = ScoutNotificationCategory.objects.get_or_create(
                    name=NEW_MESSAGE_RECEIVED)

                ScoutNotification.objects.create(category=new_message_received_notification_category, scout=scout,
                                                 payload=MessageSerializer(msg,
                                                                           context={
                                                                               'requesting_participant': receiver_participant
                                                                           }).data, display=False)

            elif receiver_participant.type == TYPE_CUSTOMER:

                new_message_received_to_customer_notification_category, _ = CustomerNotificationCategory.objects. \
                    get_or_create(name=NEW_SCOUT_MESSAGE_NC)

                customer_id = receiver_participant.customer_id
                customer = Customer.objects.using(settings.HOMES_DB).get(id=customer_id)
                from scouts.api.serializers import ScoutTaskListSerializer
                payload = {"message_id": msg.id, 'task_id': ScoutTaskListSerializer(msg.conversation.task).data}
                cm = CustomerNotification(category=new_message_received_to_customer_notification_category,
                                          customer_id=customer_id,
                                          payload=payload, display=False)

                cm.save(data={"scout_name": str(customer.name), 'message': msg.content})


# remove later
def send_message_to_receiver_participant_via_socket(data, receiver_participant):
    try:
        request_data = {'data': data, 'receiver_socket_id': receiver_participant.socket_clients.first().socket_id,
                        'server_password': config('NODEJS_SERVER_PASSWORD')}
        x = requests.post(NODE_SERVER_CHAT_ENDPOINT, data=request_data)
        sentry_debug_logger.info('response is ' + str(x) + str(x.content))
        return x.status_code
    except Exception as E:
        sentry_debug_logger.info('exception is' + str(E))
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

            message_data = MessageSerializer(msg, context=self.get_serializer_context()).data
            send_message_to_receiver_participant_via_consumer_app(msg=msg, data=message_data,
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
