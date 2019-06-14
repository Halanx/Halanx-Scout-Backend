import json

from decouple import config
from pyfcm import FCMNotification

from utility.random_utils import generate_random_code

notify_scout = FCMNotification(api_key=config('FCM_SERVER_KEY')).notify_single_device


def get_picture_upload_path(instance, filename):
    return "scouts/{}/pictures/{}-{}".format(instance.scout.id, generate_random_code(n=5),
                                             filename.split('/')[-1])


def get_thumbnail_upload_path(instance, filename):
    return "scouts/{}/thumbnail/{}-{}".format(instance.scout.id, generate_random_code(n=5),
                                              filename.split('/')[-1])


def get_scout_document_upload_path(instance, filename):
    return "scouts/{}/documents/{}-{}/{}-{}".format(instance.scout.id, instance.type, instance.id,
                                                    generate_random_code(n=5), filename.split('/')[-1])


def get_scout_document_thumbnail_upload_path(instance, filename):
    return "scouts/{}/documents/{}-{}/thumbnail/{}-{}".format(instance.scout.id, instance.type, instance.id,
                                                              generate_random_code(n=5), filename.split('/')[-1])


def get_scout_task_category_image_upload_path(instance, filename):
    return "scout-task-categories/{}/{}-{}".format(instance.id, generate_random_code(n=5), filename.split('/')[-1])


default_profile_pic_url = "https://{}/static/img/nopic.jpg".format(config('AWS_S3_CUSTOM_DOMAIN'))
default_profile_pic_thumbnail_url = "https://{}/static/img/nopic_small.jpg".format(config('AWS_S3_CUSTOM_DOMAIN'))

UNASSIGNED = 'unassigned'
ASSIGNED = 'assigned'
COMPLETE = 'complete'

ScoutTaskStatusCategories = ((UNASSIGNED, 'Unassigned'),
                             (ASSIGNED, 'Assigned'),
                             (COMPLETE, 'Complete'))


def send_scout_notification(scout, title, content, category, payload):
    notify_scout(registration_id=scout.gcm_id,
                 data_message={'data': json.dumps({'title': title, 'content': content,
                                                   'category': category, 'payload': payload})})
