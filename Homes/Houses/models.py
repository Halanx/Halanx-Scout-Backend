from random import randint

from django.db import models
from django.db.models import Min
from geopy import units, distance
from multiselectfield import MultiSelectField

from Homes.Houses.utils import (HouseTypeCategories, HouseFurnishTypeCategories, HouseAccomodationAllowedCategories,
                                HouseAccomodationTypeCategories, get_house_picture_upload_path,
                                SpaceAvailabilityCategories, AVAILABLE, generate_accomodation_allowed_str)
from common.models import AddressDetail


class Bed(models.Model):
    room = models.ForeignKey('SharedRoom', on_delete=models.CASCADE, related_name='beds')
    bed_no = models.CharField(max_length=10, blank=True, null=True)

    availability = models.CharField(max_length=20, default=AVAILABLE, choices=SpaceAvailabilityCategories)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.bed_no = str(self.room.beds.count() + 1)
        super(Bed, self).save(*args, **kwargs)


class SharedRoom(models.Model):
    space = models.OneToOneField('Space', on_delete=models.PROTECT, null=True, related_name='shared_room')
    bed_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return str(self.id)

    @property
    def free_bed_count(self):
        return self.beds.filter(availability=AVAILABLE, visible=True).count()


class PrivateRoom(models.Model):
    space = models.OneToOneField('Space', on_delete=models.PROTECT, null=True, related_name='private_room')

    def __str__(self):
        return str(self.id)


class Flat(models.Model):
    space = models.OneToOneField('Space', on_delete=models.PROTECT, null=True, related_name='flat')

    def __str__(self):
        return str(self.id)


class SpaceSubType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_type = models.CharField(max_length=20, choices=HouseAccomodationTypeCategories, blank=True, null=True)

    def __str__(self):
        return str(self.name)


class Space(models.Model):
    house = models.ForeignKey('House', on_delete=models.PROTECT, related_name='spaces')
    name = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=20, choices=HouseAccomodationTypeCategories)
    subtype = models.ForeignKey('SpaceSubType', on_delete=models.SET_NULL, related_name='spaces', null=True)

    rent = models.FloatField(default=0)
    security_deposit = models.FloatField(default=0)
    commission = models.FloatField(default=0)

    availability = models.CharField(max_length=20, default=AVAILABLE, choices=SpaceAvailabilityCategories)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)


class HouseManager(models.Manager):
    @staticmethod
    def nearby(latitude, longitude, distance_range=5):
        queryset = House.objects.filter(visible=True)
        rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2
        latitude, longitude = float(latitude), float(longitude)
        queryset = queryset.filter(address__latitude__range=(latitude - rough_distance, latitude + rough_distance),
                                   address__longitude__range=(longitude - rough_distance, longitude + rough_distance))
        return queryset

    @staticmethod
    def sorted_nearby(latitude, longitude, distance_range=5, queryset=None):
        if not queryset:
            queryset = HouseManager.nearby(latitude, longitude, distance_range)
        result = []
        for house in queryset:
            exact_distance = distance.distance((latitude, longitude), (house.address.latitude,
                                                                       house.address.longitude)).km
            result.append((house, exact_distance))

        result.sort(key=lambda x: x[1])
        return result


class House(models.Model):
    agreement_commencement_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    rules = models.TextField(null=True, blank=True)
    cover_pic_url = models.CharField(max_length=500, blank=True, null=True)
    preferred_food = models.CharField(max_length=200, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(auto_now_add=False, auto_now=True)
    available_from = models.DateTimeField(null=True, blank=True)
    available = models.BooleanField(default=True)
    visible = models.BooleanField(default=False)

    bhk_count = models.PositiveIntegerField(default=1)
    house_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseTypeCategories)
    furnish_type = models.CharField(max_length=25, blank=True, null=True, choices=HouseFurnishTypeCategories)
    available_accomodation_types = MultiSelectField(max_length=25, max_choices=3,
                                                    choices=HouseAccomodationTypeCategories)
    accomodation_allowed = MultiSelectField(max_length=25, max_choices=3, choices=HouseAccomodationAllowedCategories)
    house_size = models.CharField(max_length=20, blank=True, null=True)

    two_wheeler_parking_available = models.BooleanField(default=False)
    four_wheeler_parking_available = models.BooleanField(default=False)

    objects = HouseManager()

    def __str__(self):
        return "{}: {}".format(self.id, self.name)

    @property
    def flats(self):
        return Flat.objects.filter(space__house=self)

    @property
    def private_rooms(self):
        return PrivateRoom.objects.filter(space__house=self)

    @property
    def shared_rooms(self):
        return SharedRoom.objects.filter(space__house=self)

    @property
    def available_flat_count(self):
        return self.flats.filter(space__availability=AVAILABLE).count()

    @property
    def available_room_count(self):
        return self.shared_rooms.filter(space__availability=AVAILABLE).count()

    @property
    def available_bed_count(self):
        return Bed.objects.filter(room__space__house=self, availability=AVAILABLE).count()

    @property
    def rent_from(self):
        return self.spaces.filter(visible=True).aggregate(Min('rent'))['rent__min']

    @property
    def security_deposit_from(self):
        return self.spaces.filter(visible=True).aggregate(Min('security_deposit'))['security_deposit__min']

    @property
    def accomodation_allowed_str(self):
        return generate_accomodation_allowed_str(self.accomodation_allowed)

    @property
    def space_types_dict(self):
        spaces = self.spaces.filter(visible=True)
        space_types_metadata = spaces.values_list('type', 'subtype__name').distinct()
        space_types_dict = {x[0]: [y[1] for y in space_types_metadata if y[0] == x[0]] for x in space_types_metadata}
        return space_types_dict


class HouseAddressDetail(AddressDetail):
    house = models.OneToOneField('House', on_delete=models.CASCADE, related_name='address')


class HousePicture(models.Model):
    house = models.ForeignKey('House', on_delete=models.DO_NOTHING, related_name='pictures')
    image = models.ImageField(upload_to=get_house_picture_upload_path, null=True, blank=True)
    is_cover_pic = models.BooleanField(default=False)
    rank = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)


class HouseVisit(models.Model):
    house = models.ForeignKey('House', on_delete=models.SET_NULL, null=True, related_name='visits')
    # customer = models.ForeignKey('UserBase.Customer', on_delete=models.SET_NULL, null=True,
    # related_name='house_visits')
    code = models.CharField(max_length=10, blank=True, null=True)
    scheduled_visit_time = models.DateTimeField(blank=True, null=True)

    customer_rating = models.IntegerField(default=0)
    customer_feedback = models.TextField(blank=True, null=True)
    area_manager_notes = models.TextField(blank=True, null=True)
    visited = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    actual_visit_time = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        ordering = ('-scheduled_visit_time',)

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = str(randint(111111, 999999))
        super(HouseVisit, self).save(*args, **kwargs)
