from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView, get_object_or_404, RetrieveUpdateAPIView, CreateAPIView

from scouts.models import Scout, ScoutTask, ScoutSubTaskCategory
from scouts.permissions import IsScout
from scouts.sub_tasks.api.serializers import MoveOutRemarkUpdateSerializer, MoveOutAmenitiesCheckupListSerializer, \
    MoveOutAmenitiesCheckupUpdateSerializer, PropertyOnBoardingHouseAddressCreateSerializer, \
    PropertyOnBoardHouseBasicDetailsCreateSerializer, \
    PropertyOnBoardHousePhotosUploadSerializer, PropertyOnBoardHouseAmenitiesUpdateSerializer
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup, PropertyOnBoardingHousePhoto, \
    PropertyOnBoardingHouseAmenity
from scouts.utils import ASSIGNED, MOVE_OUT, PROPERTY_ONBOARDING, PROPERTY_ONBOARDING_HOUSE_ADDRESS_SUBTASK, \
    PROPERTY_ONBOARDING_HOUSE_BASIC_DETAILS_SUBTASK
from utility.render_response_utils import ERROR, STATUS


class MoveOutRemarkUpdateView(UpdateAPIView):
    serializer_class = MoveOutRemarkUpdateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), category__name=MOVE_OUT)
        return get_object_or_404(MoveOutRemark, task=scout_task, task__scout=scout, task__status=ASSIGNED)


class MoveOutAmenitiesCheckupRetrieveUpdateView(RetrieveUpdateAPIView):
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), scout=scout, category__name=MOVE_OUT)
        return get_object_or_404(MoveOutAmenitiesCheckup, task=scout_task, task__scout=scout, task__status=ASSIGNED)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return MoveOutAmenitiesCheckupListSerializer
        else:
            return MoveOutAmenitiesCheckupUpdateSerializer

    def perform_update(self, serializer):
        serializer.save(data=self.request.data['data'])


class PropertyOnBoardHouseAddressCreateView(CreateAPIView):
    serializer_class = PropertyOnBoardingHouseAddressCreateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def __init__(self):
        super(PropertyOnBoardHouseAddressCreateView, self).__init__()
        self.scout_task = None

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=self.request.user)
        self.scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), scout=scout, status=ASSIGNED,
                                            category__name=PROPERTY_ONBOARDING)
        return super(PropertyOnBoardHouseAddressCreateView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(task=self.scout_task, parent_subtask_category=ScoutSubTaskCategory.objects.get_or_create(
            name=PROPERTY_ONBOARDING_HOUSE_BASIC_DETAILS_SUBTASK, task_category=self.scout_task.category)[0])


class PropertyOnBoardHouseBasicDetailsCreateView(CreateAPIView):
    serializer_class = PropertyOnBoardHouseBasicDetailsCreateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def __init__(self):
        super(PropertyOnBoardHouseBasicDetailsCreateView, self).__init__()
        self.scout_task = None

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=self.request.user)
        self.scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), scout=scout, status=ASSIGNED,
                                            category__name=PROPERTY_ONBOARDING)
        return super(PropertyOnBoardHouseBasicDetailsCreateView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(task=self.scout_task, parent_subtask_category=ScoutSubTaskCategory.objects.get_or_create(
            name=PROPERTY_ONBOARDING_HOUSE_BASIC_DETAILS, task_category=self.scout_task.category)[0])


class PropertyOnBoardHousePhotosUploadView(CreateAPIView):
    serializer_class = PropertyOnBoardHousePhotosUploadSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def __init__(self):
        super(PropertyOnBoardHousePhotosUploadView, self).__init__()
        self.scout_task = None

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=self.request.user)
        self.scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), scout=scout, status=ASSIGNED,
                                            category__name=PROPERTY_ONBOARDING)
        return super(PropertyOnBoardHousePhotosUploadView, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            serializer.save(property_on_boarding_house_photo_sub_task=PropertyOnBoardingHousePhoto.objects.get(
                task=self.scout_task))
        except PropertyOnBoardingHousePhoto.DoesNotExist:
            raise ValidationError({STATUS: ERROR, 'message': 'No Property On Boarding House Photo Sub Task found'})

    def get_queryset(self):
        return PropertyOnBoardingHousePhoto.objects.filter(task=self.scout_task)


class PropertyOnBoardHouseAmenitiesUpdateView(UpdateAPIView):
    serializer_class = PropertyOnBoardHouseAmenitiesUpdateSerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication)
    permission_classes = (IsScout,)

    def get_object(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        scout_task = get_object_or_404(ScoutTask, id=self.kwargs.get('task_id'), scout=scout,
                                       category__name=PROPERTY_ONBOARDING)
        return get_object_or_404(PropertyOnBoardingHouseAmenity, task=scout_task, task__scout=scout,
                                 task__status=ASSIGNED)

    def perform_update(self, serializer):
        serializer.save(data=self.request.data['data'])

