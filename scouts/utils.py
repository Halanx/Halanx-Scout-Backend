from decouple import config
from geopy import units, distance
from pyfcm import FCMNotification

from HalanxScout import settings
from Homes.Houses.models import House
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


def get_nearby_scouts(latitude, longitude, distance_range=5, queryset=None):
    from scouts.models import Scout
    if queryset is None:
        queryset = Scout.objects.all()
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2
    latitude, longitude = float(latitude), float(longitude)
    queryset = queryset.filter(work_address__latitude__range=(latitude - rough_distance, latitude + rough_distance),
                               work_address__longitude__range=(longitude - rough_distance, longitude + rough_distance))
    return queryset


def get_sorted_scouts_nearby(house_latitude, house_longitude, distance_range=10, queryset=None):
    if queryset is None:
        from scouts.models import Scout
        queryset = Scout.objects.all()

    queryset = get_nearby_scouts(house_latitude, house_longitude, distance_range, queryset)

    result = []
    for scout in queryset:
        exact_distance = distance.distance((house_latitude, house_longitude), (scout.work_address.latitude,
                                                                               scout.work_address.longitude)).km
        result.append((scout, exact_distance))

    result.sort(key=lambda x: x[1])
    return result


def get_appropriate_scout_for_the_house_visit_task(task, scouts=None):
    # TODO
    from scouts.models import ScoutTaskAssignmentRequest
    from scouts.models import Scout

    if scouts is None:
        scouts = Scout.objects.all()

    # DEMO_TESTING = True
    DEMO_TESTING = False

    rejected_scouts_id = ScoutTaskAssignmentRequest.objects.filter(task=task, status=REQUEST_REJECTED). \
        values_list('scout', flat=True)
    scouts = scouts.exclude(id__in=rejected_scouts_id)

    if DEMO_TESTING:
        try:
            selected_scout = scouts.get(id=5)  # Ashish Rawat
        except Exception as E:
            sentry_debug_logger.debug("error while selecting Ashish" + str(E))
            selected_scout = scouts.get(id=8)  # Mayank verma

    else:
        house = House.objects.using(settings.HOMES_DB).get(id=task.house_id)
        sorted_scouts = get_sorted_scouts_nearby(house_latitude=house.address.latitude,
                                                 house_longitude=house.address.longitude,
                                                 distance_range=15, queryset=scouts)

        try:
            selected_scout = sorted_scouts[0][0]
        except Exception as E:
            sentry_debug_logger.debug('error in non demo testing is  ' + str(E), exc_info=True)
            selected_scout = None

    sentry_debug_logger.debug("received scout is " + str(selected_scout))

    return selected_scout
