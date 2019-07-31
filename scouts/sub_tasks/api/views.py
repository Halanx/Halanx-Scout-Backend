from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import UpdateAPIView, get_object_or_404

from scouts.models import Scout, ScoutTask
from scouts.permissions import IsScout
from scouts.sub_tasks.api.serializers import MoveOutRemarkUpdateSerializer
from scouts.sub_tasks.models import MoveOutRemark
from scouts.utils import ASSIGNED


class MoveOutRemarkUpdateView(UpdateAPIView):
    serializer_class = MoveOutRemarkUpdateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout, )

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'))
        return get_object_or_404(MoveOutRemark, task=scout_task, task__scout=scout, task__status=ASSIGNED)

