from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header

from chat.utils import TYPE_CUSTOMER, TYPE_SCOUT


class CustomerAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.using(settings.HOMES_DB).select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token


class ChatParticipantAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token, request)

    # noinspection PyMethodOverriding
    def authenticate_credentials(self, key, request):
        model = self.get_model()
        try:
            if request.META["HTTP_PARTICIPANT_TYPE"] == TYPE_CUSTOMER:
                token = model.objects.using(settings.HOMES_DB).select_related('user').get(key=key)

            elif request.META["HTTP_PARTICIPANT_TYPE"] == TYPE_SCOUT:
                token = model.objects.select_related('user').get(key=key)

            else:
                raise exceptions.AuthenticationFailed(
                    _('type can be one of the available choices: ' + TYPE_SCOUT + "," +
                      TYPE_CUSTOMER))

        except KeyError:
            raise exceptions.AuthenticationFailed(_("No 'PARTICIPANT-TYPE' header found"))

        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token
