from django.db import models

from Homes.Bookings.utils import BOOKING_COMPLETE
from common.models import AddressDetail


class Tenant(models.Model):
    customer = models.OneToOneField('UserBase.Customer', on_delete=models.PROTECT, related_name='tenant')

    def __str__(self):
        return "{}: {}".format(self.id, self.customer.name)

    @property
    def name(self):
        return self.customer.name

    @property
    def phone_no(self):
        return self.customer.phone_no

    @property
    def current_booking(self):
        return self.bookings.select_related('space', 'space__house', 'space__house__address').filter(
            status=BOOKING_COMPLETE, moved_out=False).first()


class TenantPermanentAddressDetail(AddressDetail):
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE, related_name='permanent_address')


class TenantMoveOutRequest(models.Model):
    tenant = models.ForeignKey(Tenant, null=True, on_delete=models.SET_NULL, related_name='moveout_requests')
    timing = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
