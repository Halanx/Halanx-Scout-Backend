from rest_framework import serializers

from Homes.Bookings.models import Booking
from Homes.Houses.serializers import SpaceSerializer


class BookingSerializer(serializers.ModelSerializer):
    space = SpaceSerializer()

    class Meta:
        model = Booking
        fields = '__all__'
