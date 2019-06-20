import random
from datetime import timedelta, datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, exceptions
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView, CreateAPIView, ListCreateAPIView, \
    RetrieveUpdateDestroyAPIView, DestroyAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from Homes.Tenants.models import Tenant
from Homes.Tenants.serializers import TenantSerializer
from common.utils import DATETIME_SERIALIZER_FORMAT, PAID, PENDING
from scouts.api.serializers import ScoutSerializer, ScoutPictureSerializer, ScoutDocumentSerializer, \
    ScheduledAvailabilitySerializer, ScoutNotificationSerializer, ChangePasswordSerializer, ScoutWalletSerializer, \
    ScoutPaymentSerializer, ScoutTaskListSerializer, ScoutTaskDetailSerializer
from scouts.models import OTP, Scout, ScoutPicture, ScoutDocument, ScheduledAvailability, ScoutNotification, \
    ScoutWallet, ScoutPayment, ScoutTask, ScoutTaskAssignmentRequest
from scouts.utils import ASSIGNED, COMPLETE, UNASSIGNED, REQUEST_REJECTED, REQUEST_AWAITED, REQUEST_ACCEPTED
from utility.sms_utils import send_sms


class AuthenticatedRequestMixin(object):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, TokenAuthentication]


class TenantAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.using(settings.HOMES_DB).select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token


@api_view(['POST'])
def register(request):
    """
    post:
    Register a new user as scout
    required fields: first_name, last_name, phone_no, otp, password
    optional fields: email
    """
    # check if all required fields provided
    required = ['first_name', 'last_name', 'phone_no', 'otp', 'password']
    if not all([request.data.get(field) for field in required]):
        return Response({"error": "Incomplete fields provided!"}, status=status.HTTP_400_BAD_REQUEST)

    # validate otp
    otp = get_object_or_404(OTP, phone_no=request.data.get('phone_no'))
    if request.data.get('otp') != otp.password:
        return Response({"error": "Wrong OTP!"}, status=status.HTTP_400_BAD_REQUEST)

    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    phone_no = request.data.get('phone_no')
    email = request.data.get('email')
    password = request.data.get('password')
    username = "s{}".format(phone_no)

    # check if scout has unique phone number
    if Scout.objects.filter(phone_no=phone_no).exists():
        return Response({"error": "Scout with this Phone Number already exists!"}, status=status.HTTP_409_CONFLICT)

    # create scout user
    try:
        user = User.objects.create_user(username=username, password=password, email=email,
                                        first_name=first_name, last_name=last_name)
    except IntegrityError:
        user = User.objects.get(username=username)
    if user.pk is None:
            return Response({"error": "New user could not be created."}, status=status.HTTP_400_BAD_REQUEST)

    # create scout
    Scout.objects.create(user=user, phone_no=phone_no)

    # generate auth token
    token, created = Token.objects.get_or_create(user=user)
    return Response({"key": token.key}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def generate_otp(request, phone_no):
    """
    post:
    Generate OTP for requested mobile number
    """
    rand = random.randrange(1, 8999) + 1000
    message = "Hi {}! {} is your One Time Password(OTP) for Halanx Scout App.".format(
        request.data.get('first_name', ''), rand)
    otp, created = OTP.objects.get_or_create(phone_no=phone_no)
    otp.password = rand
    otp.save()

    send_sms.delay(phone_no, message)
    return Response({"result": "success"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def login_with_otp(request):
    """
    post:
    Generate token for user
    """
    phone_no = request.data.get('username')[1:]
    scout = get_object_or_404(Scout, phone_no=phone_no)
    user = scout.user
    otp = get_object_or_404(OTP, phone_no=phone_no, password=request.data.get('password'))
    if otp.timestamp >= timezone.now() - timedelta(minutes=10):
        token, created = Token.objects.get_or_create(user=user)
        return Response({"key": token.key}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(AuthenticatedRequestMixin, UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User

    def update(self, request, *args, **kwargs):
        """
        change password of scout either by old password or otp
        """
        user = request.user
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            otp = serializer.data.get("otp")
            old_password = serializer.data.get("old_password")
            new_password = serializer.data.get("new_password")

            if not old_password and not otp:
                msg = "Require either old password or otp"
                raise ValidationError(msg)

            if old_password and not user.check_password(old_password):
                msg = "Wrong old password."
                raise ValidationError(msg)

            if otp:
                scout = get_object_or_404(Scout, user=request.user)
                otp = get_object_or_404(OTP, phone_no=scout.phone_no, password=otp)
                if not otp.timestamp >= timezone.now() - timedelta(minutes=10):
                    msg = "OTP has expired"
                    raise ValidationError(msg)

            user.set_password(new_password)
            user.save()
            return Response({'detail': "success"}, status=status.HTTP_200_OK)

        msg = serializer.errors
        raise ValidationError(msg)


class ScoutRetrieveUpdateView(AuthenticatedRequestMixin, RetrieveUpdateAPIView):
    serializer_class = ScoutSerializer
    queryset = Scout.objects.all()

    def get_object(self):
        return get_object_or_404(Scout, user=self.request.user)


class ScoutPictureCreateView(AuthenticatedRequestMixin, CreateAPIView):
    serializer_class = ScoutPictureSerializer
    queryset = ScoutPicture.objects.all()

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=request.user)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scout=scout, is_profile_pic=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoutDocumentListCreateView(AuthenticatedRequestMixin, ListCreateAPIView):
    serializer_class = ScoutDocumentSerializer
    queryset = ScoutDocument.objects.all()

    def get_queryset(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        return scout.latest_documents

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=request.user)
        serializer = ScoutDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scout=scout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoutDocumentDestroyView(AuthenticatedRequestMixin, DestroyAPIView):
    queryset = ScoutDocument.objects.all()

    def get_object(self):
        return get_object_or_404(ScoutDocument, pk=self.kwargs.get('pk'), is_deleted=False)

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class ScheduledAvailabilityListCreateView(AuthenticatedRequestMixin, ListCreateAPIView):
    serializer_class = ScheduledAvailabilitySerializer
    queryset = ScheduledAvailability.objects.all()

    def get_queryset(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        return scout.scheduled_availabilities.order_by('start_time').filter(start_time__gte=timezone.now(),
                                                                            cancelled=False)

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=request.user)
        start_time = datetime.strptime(request.data.get('start_time'), DATETIME_SERIALIZER_FORMAT)
        end_time = datetime.strptime(request.data.get('end_time'), DATETIME_SERIALIZER_FORMAT)
        if scout.scheduled_availabilities.filter(start_time__lte=start_time, end_time__gte=end_time).count():
            return Response({'error': 'A scheduled availability already exists in given time range'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scout=scout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduledAvailabilityRetrieveUpdateDestroyView(AuthenticatedRequestMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = ScheduledAvailabilitySerializer
    queryset = ScheduledAvailability.objects.all()

    def get_object(self):
        return get_object_or_404(ScheduledAvailability, pk=self.kwargs.get('pk'), scout__user=self.request.user,
                                 cancelled=False, start_time__gte=timezone.now())

    def perform_destroy(self, instance):
        instance.cancelled = True
        instance.save()


class ScoutNotificationListView(AuthenticatedRequestMixin, ListAPIView):
    serializer_class = ScoutNotificationSerializer
    queryset = ScoutNotification.objects.all()

    def list(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=self.request.user)
        queryset = scout.notifications.filter(display=True).order_by('-timestamp').all()[:30]
        data = self.get_serializer(queryset, many=True).data
        scout.notifications.all().update(seen=True)
        return Response(data, status=status.HTTP_200_OK)


class ScoutWalletRetrieveView(AuthenticatedRequestMixin, RetrieveAPIView):
    serializer_class = ScoutWalletSerializer
    queryset = ScoutWallet.objects.all()

    def get_object(self):
        return get_object_or_404(ScoutWallet, scout__user=self.request.user)


class ScoutPaymentListView(AuthenticatedRequestMixin, ListAPIView):
    serializer_class = ScoutPaymentSerializer
    queryset = ScoutPayment.objects.all()

    def get_queryset(self):
        wallet = get_object_or_404(ScoutWallet, scout__user=self.request.user)
        payments = wallet.payments.all().order_by('-timestamp')
        payment_status = self.request.GET.get('status')
        if payment_status in [PAID, PENDING]:
            payments = payments.filter(status=payment_status)
        return payments


class ScoutTaskListView(AuthenticatedRequestMixin, ListAPIView):
    serializer_class = ScoutTaskListSerializer
    queryset = ScoutTask.objects.all()

    def get_queryset(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        return scout.tasks.filter(status=ASSIGNED).order_by('scheduled_at')


class ScoutTaskRetrieveUpdateDestroyAPIView(AuthenticatedRequestMixin, RetrieveUpdateDestroyAPIView):
    serializer_class = ScoutTaskDetailSerializer
    queryset = ScoutTask.objects.all()

    def get_object(self):
        return get_object_or_404(ScoutTask, pk=self.kwargs.get('pk'), scout__user=self.request.user,
                                 status=ASSIGNED)

    def update(self, request, *args, **kwargs):
        data = request.POST
        task = self.get_object()
        if data.get('complete'):
            task.status = COMPLETE
        if data.get('remark'):
            task.remark = data['remark']
        task.save()
        return Response(status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        task = self.get_object()
        assignment_request = task.assignment_requests.filter(scout=task.scout).last()
        if assignment_request:
            assignment_request.status = REQUEST_REJECTED
            assignment_request.save()
        task.status = UNASSIGNED
        task.scout = None
        task.save()


class ScoutTaskAssignmentRequestUpdateAPIView(AuthenticatedRequestMixin, UpdateAPIView):
    serializer_class = None
    queryset = ScoutTaskAssignmentRequest.objects.all()

    def get_object(self):
        task = get_object_or_404(ScoutTask, pk=self.kwargs.get('pk'), status=UNASSIGNED)
        assignment_request = task.assignment_requests.filter(scout__user=self.request.user,
                                                             status=REQUEST_AWAITED).last()
        if assignment_request:
            return assignment_request
        else:
            raise Http404

    def update(self, request, *args, **kwargs):
        assignment_request = self.get_object()
        data = request.data
        if data.get('status') in [REQUEST_ACCEPTED, REQUEST_REJECTED]:
            assignment_request.status = data.get('status')
            assignment_request.save()
        return Response({'detail': data.get('status')})


class TenantRetrieveView(RetrieveAPIView):
    serializer_class = TenantSerializer
    queryset = Tenant.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [TenantAuthentication]

    def get_object(self):
        return get_object_or_404(Tenant.objects.using(settings.HOMES_DB), customer__user=self.request.user)
