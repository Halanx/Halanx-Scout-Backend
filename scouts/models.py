from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Scout(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    phone_no = models.CharField(max_length=30, unique=True, validators=[RegexValidator('^[+]*\d{10,}$',
                                                                                       message="Phone Number should "
                                                                                               "contain at least 10 "
                                                                                               "numeric characters")])

    def __str__(self):
        return str(self.id)

    @property
    def name(self):
        return self.user.get_full_name()


class OTP(models.Model):
    phone_no = models.CharField(max_length=30)
    password = models.IntegerField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
