from django.contrib.auth.models import User
from rest_framework import serializers

from scouts.models import Scout, ScoutDocument, ScoutPermanentAddress, ScoutWorkAddress, ScoutBankDetail, ScoutPicture


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
        read_only_fields = ('phone_no', )

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
            super(ScoutPermanentAddressSerializer, permanent_address_serializer)\
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
        fields = ('image', )
