import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.utils import DocumentTypeCategories
from scouts.api.serializers import ScoutSerializer, ScoutPictureSerializer, ScoutDocumentSerializer
from scouts.models import OTP, Scout, ScoutPicture, ScoutDocument
from utility.sms_utils import send_sms


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


class ScoutRetrieveUpdateView(RetrieveUpdateAPIView):
    serializer_class = ScoutSerializer
    queryset = Scout.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def get_object(self):
        return get_object_or_404(Scout, user=self.request.user)


class ScoutPictureCreateView(CreateAPIView):
    serializer_class = ScoutPictureSerializer
    queryset = ScoutPicture.objects.all()
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [BasicAuthentication, TokenAuthentication]

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=request.user)
        serializer = ScoutPictureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scout=scout, is_profile_pic=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScoutDocumentListCreateView(ListCreateAPIView):
    serializer_class = ScoutDocumentSerializer
    queryset = ScoutDocument.objects.all()

    def get_queryset(self):
        scout = get_object_or_404(Scout, user=self.request.user)
        documents = scout.documents.order_by('-id')
        latest_documents = []
        for doc_type in list(zip(*DocumentTypeCategories))[0]:
            latest_documents.append(documents.filter(type=doc_type).first())
        return list(filter(lambda x: x is not None, latest_documents))

    def create(self, request, *args, **kwargs):
        scout = get_object_or_404(Scout, user=request.user)
        serializer = ScoutDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(scout=scout)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
