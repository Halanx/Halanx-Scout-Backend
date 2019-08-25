from django.db import models

from Homes.Bookings.utils import BookingStatusCategories, BOOKING_PARTIAL, TOKEN_AMOUNT, ONBOARDING_CHARGES, \
    NEW_TENANT_BOOKING, BookingTypeCategories, FacilityItemTypeCategories, BookingFacilityStatusChoices, \
    FACILITY_ALLOCATED


class Booking(models.Model):
    space = models.ForeignKey('Houses.Space', null=True, on_delete=models.SET_NULL, related_name="bookings")
    tenant = models.ForeignKey('Tenants.Tenant', null=True, on_delete=models.SET_NULL, related_name="bookings")
    type = models.CharField(max_length=50, default=NEW_TENANT_BOOKING, choices=BookingTypeCategories)
    status = models.CharField(max_length=200, default=BOOKING_PARTIAL, choices=BookingStatusCategories)
    license_start_date = models.DateTimeField(null=False, blank=False)
    license_end_date = models.DateTimeField(null=True, blank=True)
    lock_in_period = models.IntegerField(blank=True, null=True, default=6)

    rent = models.FloatField(default=0)
    security_deposit = models.FloatField(default=0)
    token_amount = models.FloatField(default=TOKEN_AMOUNT)
    onboarding_charges = models.FloatField(default=ONBOARDING_CHARGES)

    paid_token_amount = models.BooleanField(default=False)
    paid_movein_charges = models.BooleanField(default=False)

    moved_out = models.BooleanField(default=False)
    move_in_notes = models.TextField(blank=True, null=True)
    move_out_notes = models.TextField(blank=True, null=True)
    area_manager_notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ('license_start_date',)


class FacilityItem(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=15, blank=True, null=True, choices=FacilityItemTypeCategories)

    def __str__(self):
        return self.name


class BookingFacility(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, null=True, related_name='facilities')
    item = models.ForeignKey('FacilityItem', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    quantity_acknowledged = models.IntegerField(default=0)
    remark = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=50, choices=BookingFacilityStatusChoices, default=FACILITY_ALLOCATED)

    class Meta:
        verbose_name_plural = 'Booking Facilities'

    def __str__(self):
        return "{} x {}".format(self.item, self.quantity)