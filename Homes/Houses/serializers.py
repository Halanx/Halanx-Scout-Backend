from rest_framework import serializers

from Homes.Houses.models import HouseAddressDetail, House


class HouseAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAddressDetail
        fields = '__all__'


class HouseSerializer(serializers.ModelSerializer):
    address = HouseAddressDetailSerializer()

    class Meta:
        model = House
        fields = ('id', 'name', 'address', 'cover_pic_url')
