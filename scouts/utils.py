from decouple import config
from pyfcm import FCMNotification

from utility.logging_utils import sentry_debug_logger
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


REQUEST_ACCEPTED = 'accepted'
REQUEST_REJECTED = 'rejected'
REQUEST_AWAITED = 'awaited'

ScoutTaskAssignmentRequestStatusCategories = (
    (REQUEST_ACCEPTED, 'Accepted'),
    (REQUEST_REJECTED, 'Rejected'),
    (REQUEST_AWAITED, 'Awaited')
)

# predefined scout notification categories
NEW_TASK_NOTIFICATION = 'NewTask'
TASK_TYPE = 'Task Type'
HOUSE_VISIT = 'House Visit'


def get_appropriate_scout_for_the_house_visit_task(task, scouts=None):
    # TODO
    from scouts.models import ScoutTaskAssignmentRequest
    from scouts.models import Scout

    if scouts is None:
        scouts = Scout.objects.all()
    # scouts = random.choice(scouts)
    # selected_scout = random.choice(scouts)
    rejected_scouts_id = ScoutTaskAssignmentRequest.objects.filter(task=task, status=REQUEST_REJECTED). \
        values_list('scout', flat=True)
    scouts = scouts.exclude(id__in=rejected_scouts_id)
    try:
        selected_scout = scouts.get(id=5)  # Ashish Rawat
    except Exception as E:
        sentry_debug_logger.debug("error while selecting Ashish")
        selected_scout = scouts.get(id=8)  # Mayank Rawat

    sentry_debug_logger.debug("received scout id is " + str(selected_scout.id))
    return selected_scout
