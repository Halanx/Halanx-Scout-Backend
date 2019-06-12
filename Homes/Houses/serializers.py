from rest_framework import serializers

from Homes.Houses.models import HouseAddressDetail, House, Space


class HouseAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = HouseAddressDetail
        fields = '__all__'


class HouseSerializer(serializers.ModelSerializer):
    address = HouseAddressDetailSerializer()

    class Meta:
        model = House
        fields = ('id', 'name', 'address', 'cover_pic_url')


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ('id', 'name', 'type')


class SpaceDetailSerializer(serializers.ModelSerializer):
    house = HouseSerializer()

    class Meta:
        model = Space
        fields = ('id', 'name', 'house')
