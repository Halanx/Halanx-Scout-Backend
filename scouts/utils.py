from decouple import config

from utility.random_utils import generate_random_code


def get_picture_upload_path(instance, filename):
    return "affiliates/{}/pictures/{}-{}".format(instance.scout.id, generate_random_code(n=5),
                                                 filename.split('/')[-1])


def get_thumbnail_upload_path(instance, filename):
    return "affiliates/{}/thumbnail/{}-{}".format(instance.scout.id, generate_random_code(n=5),
                                                  filename.split('/')[-1])


default_profile_pic_url = "https://{}/static/img/nopic.jpg".format(config('AWS_S3_CUSTOM_DOMAIN'))
default_profile_pic_thumbnail_url = "https://{}/static/img/nopic_small.jpg".format(config('AWS_S3_CUSTOM_DOMAIN'))
