from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from Homes.Bookings.models import Booking
from Homes.Houses.models import House, HouseVisit
from Homes.Houses.serializers import HouseSerializer, SpaceSerializer
from UserBase.serializers import CustomerSerializer
from chat.api.serializers import ScoutDetailSerializer
from common.utils import DATETIME_SERIALIZER_FORMAT
from scouts.models import Scout, ScoutDocument, ScoutPermanentAddress, ScoutWorkAddress, ScoutBankDetail, ScoutPicture, \
    ScheduledAvailability, ScoutNotification, ScoutNotificationCategory, ScoutWallet, ScoutPayment, ScoutTask, \
    ScoutTaskCategory, ScoutSubTaskCategory, ScoutTaskReviewTagCategory
from utility.serializers import DateTimeFieldTZ


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


# noinspection PyAbstractClass
class ChangePasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True, allow_null=True)
    old_password = serializers.CharField(required=True, allow_null=True)
    new_password = serializers.CharField(required=True)


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


class ScoutTaskReviewTagCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutTaskReviewTagCategory
        fields = '__all__'


class ScoutSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    permanent_address = ScoutPermanentAddressSerializer()
    work_address = ScoutWorkAddressSerializer()
    bank_detail = ScoutBankDetailSerializer()
    document_submission_complete = serializers.ReadOnlyField()
    bank_details_complete = serializers.ReadOnlyField()
    review_tags = ScoutTaskReviewTagCategorySerializer(many=True)

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


class ScoutWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutWallet
        fields = ('credit', 'pending_withdrawal', 'debit')


class ScoutPaymentSerializer(serializers.ModelSerializer):
    paid_on = serializers.DateTimeField(format='%d %B, %Y')

    class Meta:
        model = ScoutPayment
        exclude = ('due_date', 'timestamp', 'updated')


class ScoutTaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutTaskCategory
        fields = '__all__'


class ScoutSubTaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoutSubTaskCategory
        fields = ('name',)


class ScoutTaskListSerializer(serializers.ModelSerializer):
    scheduled_at = DateTimeFieldTZ(format=DATETIME_SERIALIZER_FORMAT)
    category = ScoutTaskCategorySerializer()
    house = serializers.SerializerMethodField()
    space = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = ScoutTask
        fields = ('id', 'scout', 'category', 'earning', 'scheduled_at', 'house', 'space', 'customer', 'conversation')

    @staticmethod
    def get_house(obj):
        house = House.objects.using(settings.HOMES_DB).filter(id=obj.house_id).first()
        if house:
            return HouseSerializer(house).data

    @staticmethod
    def get_space(obj):
        if obj.booking_id:
            booking = Booking.objects.using(settings.HOMES_DB).filter(id=obj.booking_id).first()
            if booking:
                space = booking.space
                return SpaceSerializer(space).data

    @staticmethod
    def get_customer(obj):
        customer = None
        if obj.visit_id:
            visit = HouseVisit.objects.using(settings.HOMES_DB).filter(id=obj.visit_id).first()
            if visit:
                customer = visit.customer
        elif obj.booking_id:
            booking = Booking.objects.using(settings.HOMES_DB).filter(id=obj.booking_id).first()
            if booking:
                customer = booking.tenant.customer
        if customer:
            return CustomerSerializer(customer).data


class ScoutTaskDetailSerializer(ScoutTaskListSerializer):
    sub_tasks = ScoutSubTaskCategorySerializer(many=True)

    class Meta:
        model = ScoutTask
        fields = ScoutTaskListSerializer.Meta.fields + ('sub_tasks', 'review_tags', 'remark')


class NewScoutTaskNotificationSerializer(serializers.ModelSerializer):
    scheduled_at = DateTimeFieldTZ(format=DATETIME_SERIALIZER_FORMAT)
    category = ScoutTaskCategorySerializer()

    class Meta:
        model = ScoutTask
        fields = ('id', 'category', 'scheduled_at')


class ScoutTaskForHouseVisitSerializer(serializers.ModelSerializer):
    scout = ScoutDetailSerializer()

    class Meta:
        model = ScoutTask
        fields = ('scout', 'category', 'status', 'house_id', 'visit_id', 'booking_id', 'scheduled_at', 'assigned_at',
                  'completed_at')
