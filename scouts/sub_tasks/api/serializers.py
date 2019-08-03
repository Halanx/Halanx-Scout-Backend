import json

import sys
import traceback

from multiselectfield.db import fields
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import MultipleChoiceField

from Homes.Houses.utils import HouseAccomodationTypeCategories
from scouts.sub_tasks.api.validators import validate_amenity_id
from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup, PropertyOnBoardingHouseAddress, \
    PropertyOnBoardingHouseBasicDetail, PropertyOnBoardingHouseAmenity, PropertyOnBoardingHousePhoto, \
    PropertyOnBoardingPhoto
from scouts.sub_tasks.utils import OK, DAMAGED, MISSING
from utility.logging_utils import sentry_debug_logger
from utility.serializers import JSONSerializerField


class MoveOutRemarkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoveOutRemark
        exclude = ('task', 'parent_subtask_category', 'parent_task_category')


class MoveOutAmenitiesCheckupListSerializer(serializers.ModelSerializer):
    amenities_json = serializers.JSONField()

    class Meta:
        model = MoveOutAmenitiesCheckup
        exclude = ('task', 'parent_subtask_category', 'parent_task_category')


class MoveOutAmenitiesCheckupUpdateSerializer(serializers.ModelSerializer):
    amenities_json = serializers.JSONField()

    class Meta:
        model = MoveOutAmenitiesCheckup
        exclude = ('task', 'parent_subtask_category', 'parent_task_category')

    def update(self, instance, validated_data):
        try:
            original_amenities_list = instance.amenities_json['data']['amenities_dict']
            amenities_patch_list = validated_data['data']['amenities_dict']

            for i in amenities_patch_list:
                amenity_id = str(amenities_patch_list[str(i)]['id'])
                if str(amenity_id) != str(i):
                    raise ValidationError({'error': 'Inconistent Data'})

                amenity_patch_data = amenities_patch_list[amenity_id]

                if amenity_id in original_amenities_list:
                    if amenity_patch_data['status'] not in [OK, DAMAGED, MISSING]:
                        raise ValidationError({'error': 'status must be one of ok, damaged or missing'})

                    original_amenities_list[amenity_id]['status'] = amenity_patch_data['status']

                    validate_amenity_id(amenity_id)

                else:
                    raise ValidationError({'detail': 'Specified Amenity Does Not Exist'})

        except ValidationError as E:
            raise E

        except Exception:
            sentry_debug_logger.error("error in updating scout move out amenity checkup", exc_info=True)
            raise ValidationError({'detail': 'Bad Request'}, code=400)

        return super(MoveOutAmenitiesCheckupUpdateSerializer, self).update(instance, validated_data)


class PropertyOnBoardingHouseAddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOnBoardingHouseAddress
        exclude = ('parent_subtask_category', 'parent_task_category')


class PropertyOnBoardHousePhotosUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyOnBoardingPhoto
        fields = '__all__'


class PropertyOnBoardHouseAmenitiesUpdateSerializer(serializers.ModelSerializer):
    amenities_json = serializers.JSONField()

    class Meta:
        model = PropertyOnBoardingHouseAmenity
        exclude = ('parent_subtask_category', 'parent_task_category')

    def update(self, instance, validated_data):
        print(validated_data)
        try:
            original_amenities_list = instance.amenities_json['data']['amenities_dict']
            amenities_patch_list = validated_data['data']['amenities_dict']

            for i in amenities_patch_list:
                amenity_id = str(amenities_patch_list[str(i)]['id'])
                if str(amenity_id) != str(i):
                    raise ValidationError({'error': 'Inconistent Data'})

                validate_amenity_id(amenity_id)

                amenity_patch_data = amenities_patch_list[amenity_id]
                original_amenities_list[amenity_id] = amenity_patch_data

        except ValidationError as E:
            raise E

        except Exception:
            sentry_debug_logger.error("error in updating scout property on board amenity lising", exc_info=True)
            raise ValidationError({'detail': 'Bad Request'}, code=400)

        return super(PropertyOnBoardHouseAmenitiesUpdateSerializer, self).update(instance, validated_data)


class PropertyOnBoardHouseBasicDetailsCreateSerializer(serializers.ModelSerializer):
    space_type = MultipleChoiceField(choices=HouseAccomodationTypeCategories)

    class Meta:
        model = PropertyOnBoardingHouseBasicDetail
        exclude = ('parent_subtask_category', 'parent_task_category')
