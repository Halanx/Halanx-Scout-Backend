from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.generics import UpdateAPIView, get_object_or_404, RetrieveUpdateAPIView, CreateAPIView

from scouts.models import Scout, ScoutTask
from scouts.permissions import IsScout
from scouts.sub_tasks.api.serializers import MoveOutRemarkUpdateSerializer, MoveOutAmenitiesCheckupListSerializer, \
    MoveOutAmenitiesCheckupUpdateSerializer
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup
from scouts.utils import ASSIGNED


class MoveOutRemarkUpdateView(UpdateAPIView):
    serializer_class = MoveOutRemarkUpdateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'))
        return get_object_or_404(MoveOutRemark, task=scout_task, task__scout=scout, task__status=ASSIGNED)


class MoveOutAmenitiesCheckupRetrieveUpdateView(RetrieveUpdateAPIView):
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'))
        return get_object_or_404(MoveOutAmenitiesCheckup, task=scout_task, task__scout=scout, task__status=ASSIGNED)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MoveOutAmenitiesCheckupListSerializer
        else:
            return MoveOutAmenitiesCheckupUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(data=self.request.data['data'])


class PropertyOnBoardHouseAddressCreateView(CreateAPIView):
    pass


class PropertyOnBoardHouseBasicDetailsCreateView(CreateAPIView):
    pass


class PropertyOnBoardHousePhotosCreateView(CreateAPIView):
    pass


class PropertyOnBoardHouseAmenitiesCreateView(CreateAPIView):
    pass
