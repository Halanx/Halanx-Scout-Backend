TOKEN_AMOUNT = 200.0
ONBOARDING_CHARGES = 200.0
LATE_MONTHLY_RENT_FINE_AMOUNT = 150

NEW_TENANT_BOOKING = 'new_tenant_booking'
EXISTING_TENANT_BOOKING = 'existing_tenant_booking'

BookingTypeCategories = (
    (NEW_TENANT_BOOKING, 'New Tenant Booking'),
    (EXISTING_TENANT_BOOKING, 'Existing Tenant Booking')
)

BOOKING_CANCELLED = 'cancelled'
BOOKING_COMPLETE = 'complete'
BOOKING_PARTIAL = 'partial'

BookingStatusCategories = (
    (BOOKING_CANCELLED, 'Cancelled'),
    (BOOKING_PARTIAL, 'Partially complete'),
    (BOOKING_COMPLETE, 'Complete'),
)

SUB_UNIT_ITEM = 'sub_unit'
COMMON_AREA_ITEM = 'common_area'

FacilityItemTypeCategories = (
    (SUB_UNIT_ITEM, 'Sub Unit'),
    (COMMON_AREA_ITEM, 'Common Area')
)

FACILITY_ALLOCATED = 'Allocated'
FACILITY_RETURNED = 'Returned'
FACILITY_LOST = 'Lost'
FACILITY_DAMAGED = 'Damaged'

BookingFacilityStatusChoices = (
    (FACILITY_ALLOCATED, FACILITY_ALLOCATED),
    (FACILITY_RETURNED, FACILITY_RETURNED),
    (FACILITY_LOST, FACILITY_LOST),
    (FACILITY_DAMAGED, FACILITY_DAMAGED),
)
