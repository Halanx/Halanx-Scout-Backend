from decouple import config
from pyfcm import FCMNotification

notify_customer = FCMNotification(api_key=config('FCM_SERVER_KEY')).notify_single_device
