import logging

from django.utils import timezone
from rest_framework import serializers

logger = logging.getLogger(__name__)


class DateTimeFieldTZ(serializers.DateTimeField):
    def to_representation(self, value):
        try:
            value = timezone.localtime(value)
            return super(DateTimeFieldTZ, self).to_representation(value)
        except Exception as e:
            logger.error(e)


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value
