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
