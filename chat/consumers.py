from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from rest_framework.generics import get_object_or_404

from chat.models import Conversation, Participant


# Authentication https://channels.readthedocs.io/en/latest/topics/authentication.html#

def check_whether_logged_in_participant_belongs_to_this_conversation(conv, participant):
    try:
        conv.participants.get(id=participant.id)
        return True
    except Participant.DoesNotExist:
        return False


def get_participant_from_user(current_user):
    """It finds the participation object from the current user"""

    # TODO Retrieve actual Participant from the user

    return current_user.participant


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        current_user = self.scope["user"]
        room_name = self.scope['url_route']['kwargs']['room_name']

        print(room_name)

        # This checks whether we have a Conversation with room name same sa that of
        #  specified room name in kwargs of web socket url
        conv = get_object_or_404(Conversation, chat_room_name=room_name)

        # This checks whether the currently logged in participant belongs to this conversation
        access_status = check_whether_logged_in_participant_belongs_to_this_conversation(conv,
                                                                                         get_participant_from_user(
                                                                                             current_user))

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        print("room-name:", self.room_name)
        print("group-name:", self.room_group_name)

        print("accesible by this participant=", access_status)

        if access_status:
            # Join room group
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        print("disconnecting")
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print("received message from web socket is", message)

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        print("received message from group :", message)
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
