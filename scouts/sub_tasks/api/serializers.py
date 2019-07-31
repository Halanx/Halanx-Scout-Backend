import json

import sys
import traceback

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from scouts.sub_tasks.models import MoveOutRemark, MoveOutAmenitiesCheckup
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

                else:
                    raise ValidationError({'detail': 'Specified Amenity Does Not Exist'})

        except ValidationError as E:
            raise E

        except Exception:
            sentry_debug_logger.error("error in updating scout move out amenity checkup", exc_info=True)
            raise ValidationError({'detail': 'Bad Request'}, code=400)

        return super(MoveOutAmenitiesCheckupUpdateSerializer, self).update(instance, validated_data)
