import json

from django.shortcuts import render
from django.utils.safestring import mark_safe
from rest_framework.generics import get_object_or_404

from chat.models import Conversation, Participant


def index(request):
    return render(request, 'chat/index.html', {})


def room(request, room_name):
    # get the current participant
    participant = get_object_or_404(Participant, user=request.user)

    # get the conversation with room name "room_name" and participant belongs to it as we;;
    conv = get_object_or_404(Conversation, chat_room_name=room_name, participants__in=[participant, ])

    return render(request, 'chat/room.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })
