from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from common.utils import DATETIME_SERIALIZER_FORMAT
from scouts.models import Scout, ScoutDocument, ScoutPermanentAddress, ScoutWorkAddress, ScoutBankDetail, ScoutPicture, \
    ScheduledAvailability, ScoutNotification, ScoutNotificationCategory
from utility.serializers import DateTimeFieldTZ


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


class ScoutPermanentAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutPermanentAddress
        fields = '__all__'


class ScoutWorkAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutWorkAddress
        fields = '__all__'


class ScoutBankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutBankDetail
        fields = '__all__'


class ScoutSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    permanent_address = ScoutPermanentAddressSerializer()
    work_address = ScoutWorkAddressSerializer()
    bank_detail = ScoutBankDetailSerializer()

    class Meta:
        model = Scout
        fields = '__all__'
        read_only_fields = ('phone_no',)

    def update(self, instance: Scout, validated_data):
        user_data = validated_data.pop('user', None)
        permanent_address_data = validated_data.pop('permanent_address', None)
        work_address_data = validated_data.pop('work_address', None)
        bank_detail_data = validated_data.pop('bank_detail', None)
        super(self.__class__, self).update(instance, validated_data)

        if user_data:
            user_serializer = UserSerializer()
            super(UserSerializer, user_serializer).update(instance.user, user_data)

        if permanent_address_data:
            permanent_address_serializer = ScoutPermanentAddressSerializer()
            super(ScoutPermanentAddressSerializer, permanent_address_serializer) \
                .update(instance.permanent_address, permanent_address_data)

        if work_address_data:
            work_address_serializer = ScoutWorkAddressSerializer()
            super(ScoutWorkAddressSerializer, work_address_serializer).update(instance.work_address, work_address_data)

        if bank_detail_data:
            bank_detail_serializer = ScoutBankDetailSerializer()
            super(ScoutBankDetailSerializer, bank_detail_serializer).update(instance.bank_detail, bank_detail_data)

        return instance


class ScoutDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutDocument
        exclude = ('is_deleted', 'verified')


class ScoutPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutPicture
        fields = ('image',)


class ScheduledAvailabilitySerializer(serializers.ModelSerializer):
    start_time = DateTimeFieldTZ(format=DATETIME_SERIALIZER_FORMAT, input_formats=[DATETIME_SERIALIZER_FORMAT])
    end_time = DateTimeFieldTZ(format=DATETIME_SERIALIZER_FORMAT, input_formats=[DATETIME_SERIALIZER_FORMAT])

    class Meta:
        model = ScheduledAvailability
        exclude = ('cancelled', 'created_at', 'updated_at',)
        read_only_fields = ('scout',)

    def validate(self, data):
        """
        Check the validity of start and end time
        """
        if data.get('start_time') and data['start_time'] < timezone.now():
            raise serializers.ValidationError("start time should be greater than current time")
        elif data.get('end_time') and data['end_time'] < timezone.now():
            raise serializers.ValidationError("end time should be greater than current time")
        elif data.get('start_time') and data.get('end_time') and data['start_time'] > data['end_time']:
            raise serializers.ValidationError("end time must occur after start time")
        return data


class ScoutNotificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutNotificationCategory
        fields = '__all__'


class ScoutNotificationSerializer(serializers.ModelSerializer):
    timestamp = DateTimeFieldTZ(format=DATETIME_SERIALIZER_FORMAT)
    category = ScoutNotificationCategorySerializer()

    class Meta:
        model = ScoutNotification
        fields = '__all__'

