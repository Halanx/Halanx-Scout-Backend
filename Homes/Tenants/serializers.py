from rest_framework import serializers

from Homes.Tenants.models import Tenant, TenantPermanentAddressDetail
from UserBase.serializers import CustomerSerializer


class TenantPermanentAddressDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantPermanentAddressDetail
        fields = '__all__'


class TenantDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()
    permanent_address = TenantPermanentAddressDetailSerializer()

    class Meta:
        model = Tenant
        fields = '__all__'
