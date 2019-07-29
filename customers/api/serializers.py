from rest_framework import serializers

from customers.models import CustomerNotificationCategory


class CustomerNotificationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerNotificationCategory
        fields = '__all__'
