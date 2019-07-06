from django.conf import settings

from utility.environments import DEVELOPMENT, PRODUCTION

TYPE_SCOUT = 'scout'
TYPE_CUSTOMER = 'customer'

ParticipantTypeCategories = (
    (TYPE_SCOUT, 'Scout'),
    (TYPE_CUSTOMER, 'Customer')
)

ROLE_SENDER = 'sender'
ROLE_RECEIVER = 'receiver'

SOCKET_STATUS_DISCONNECTED = 'disconnected'
SOCKET_STATUS_CONNECTED = 'connected'

ENDPOINT = '/chat/'

SCOUT_CUSTOMER_SOCKET_CHAT_CONVERSATION_PREFIX = 'SCOUTCHAT:'
HALANX_CONSUMERAPP_BASE_URL = 'https://api.halanx.com'
HALANX_SCOUT_CHAT_API_URL = HALANX_CONSUMERAPP_BASE_URL + '/chat/scout/send/'


if settings.ENVIRONMENT == DEVELOPMENT:
    SCHEME = 'http://'
    URL = '192.168.1.60'
    PORT = '3000'
    NODE_SERVER_CHAT_ENDPOINT = "{}{}:{}{}".format(SCHEME, URL, PORT, ENDPOINT)

else:  # settings.ENVIRONMENT == PRODUCTION:
    SCHEME = 'https://'
    URL = 'consumerchat.herokuapp.com'
    NODE_SERVER_CHAT_ENDPOINT = "{}{}{}".format(SCHEME, URL, ENDPOINT)
