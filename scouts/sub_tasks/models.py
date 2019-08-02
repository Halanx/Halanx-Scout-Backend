from django.db import models
from jsonfield import JSONField
from multiselectfield import MultiSelectField

from Homes.Houses.utils import HouseFurnishTypeCategories, HouseAccomodationTypeCategories
from scouts.models import ScoutTask, ScoutTaskCategory, ScoutSubTaskCategory
from scouts.sub_tasks.utils import MOVE_OUT_AMENITIES_CHECKUP_DEFAULT_JSON, \
    get_property_on_boarding_house_picture_upload_path, PROPERTY_ON_BOARD_AMENITIES_DEFAULT_JSON
from scouts.utils import MOVE_OUT, PROPERTY_ONBOARDING


#  MOVE OUT SUB TASKS

class MoveOutSubTask(models.Model):
    parent_task_category = models.ForeignKey(ScoutTaskCategory, on_delete=models.SET_NULL, to_field='name',
                                             default=MOVE_OUT, null=True)
    parent_subtask_category = models.ForeignKey(ScoutSubTaskCategory, on_delete=models.SET_NULL, null=True, blank=True)


class MoveOutAmenitiesCheckup(MoveOutSubTask):  # SubTask 1
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='move_out_amenity_checkup')

    amenities_json = JSONField(default=MOVE_OUT_AMENITIES_CHECKUP_DEFAULT_JSON)


class MoveOutRemark(MoveOutSubTask):  # SubTask 2
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='move_out_remark')

    content = models.TextField(blank=True, null=True)


# PROPERTY ON-BOARDING SUB TASKS

class PropertyOnBoardingSubTask(models.Model):
    parent_task_category = models.ForeignKey(ScoutTaskCategory, on_delete=models.SET_NULL, to_field='name',
                                             default=PROPERTY_ONBOARDING, null=True)
    parent_subtask_category = models.ForeignKey(ScoutSubTaskCategory, on_delete=models.SET_NULL, null=True, blank=True)


class PropertyOnBoardingHouseAddress(PropertyOnBoardingSubTask):  # SubTask 1
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='property_on_board_house_address')
    location = models.CharField(max_length=200, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)


class PropertyOnBoardingHousePhoto(PropertyOnBoardingSubTask):  # SubTask 2
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='property_on_board_house_photo')


class PropertyOnBoardingPhoto(models.Model):
    image = models.ImageField(upload_to=get_property_on_boarding_house_picture_upload_path)
    property_on_boarding_house_photo_sub_task = models.ForeignKey(PropertyOnBoardingHousePhoto, null=True,
                                                                  on_delete=models.SET_NULL, related_name='photos')


class PropertyOnBoardingHouseAmenity(PropertyOnBoardingSubTask):  # SubTask 3
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='property_on_board_house_amenity')
    amenities_json = JSONField(default=PROPERTY_ON_BOARD_AMENITIES_DEFAULT_JSON)


class PropertyOnBoardingHouseBasicDetail(PropertyOnBoardingSubTask):  # SubTask 4
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='property_on_board_house_basic_details')

    furnish_type = models.CharField(choices=HouseFurnishTypeCategories, max_length=30)
    space_type = MultiSelectField(max_length=25, max_choices=3, choices=HouseAccomodationTypeCategories)
    rent = models.FloatField()
