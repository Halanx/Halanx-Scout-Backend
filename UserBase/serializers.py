from django.contrib.auth.models import User
from rest_framework import serializers

from UserBase.models import Customer


class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class CustomerSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer()

    class Meta:
        model = Customer
        fields = ('id', 'user', 'phone_no', 'profile_pic_url', 'profile_pic_thumbnail_url')
