from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models

from UserBase.utils import (default_profile_pic_url,
                            default_profile_pic_thumbnail_url)


class Customer(models.Model):
    gcm_id = models.CharField(max_length=500, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    phone_no = models.CharField(max_length=30, unique=True, validators=[RegexValidator('^[+]*\d{10,}$',
                                                                                       message="Phone Number should "
                                                                                               "be contain at least "
                                                                                               "10 numeric numbers")])
    profile_pic_url = models.CharField(max_length=500, blank=True, null=True, default=default_profile_pic_url)
    profile_pic_thumbnail_url = models.CharField(max_length=500, blank=True, null=True,
                                                 default=default_profile_pic_thumbnail_url)

    def __str__(self):
        return str(self.phone_no)

    @property
    def name(self):
        return self.user.get_full_name()
