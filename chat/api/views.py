from rest_framework.generics import ListAPIView, ListCreateAPIView

from chat.models import Conversation, Message
from chat.utils import get_sender_from_request
from .serializers import ConversationListSerializer, MessageListCreateSerializer


class ConversationListAPIView(ListAPIView):
    serializer_class = ConversationListSerializer
    queryset = Conversation.objects.all()


class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = MessageListCreateSerializer

    def post(self, request, *args, **kwargs):
        # TODO when we are able to get the participant from current user set sender
        request.data["sender"] = get_sender_from_request(request, accept_sender_from_request_body=False)
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Message.objects.filter(conversation_id=self.kwargs.get('pk'))
