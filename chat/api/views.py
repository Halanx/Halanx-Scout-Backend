from rest_framework.generics import ListAPIView, ListCreateAPIView

from chat.models import Conversation, Message
from .serializers import ConversationListSerializer, MessageListCreateSerializer


class ConversationListAPIView(ListAPIView):
    serializer_class = ConversationListSerializer
    queryset = Conversation.objects.all()


class MessageListCreateAPIView(ListCreateAPIView):
    serializer_class = MessageListCreateSerializer

    def get_queryset(self):
        return Message.objects.filter(conversation_id=self.kwargs.get('pk'))