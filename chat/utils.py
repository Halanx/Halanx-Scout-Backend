
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
SCHEME = 'http://'
URL = '192.168.1.60'
PORT = '4001'
ENDPOINT = '/chat/'
NODE_SERVER_CHAT_ENDPOINT = "{}{}:{}{}".format(SCHEME, URL, PORT, ENDPOINT)
