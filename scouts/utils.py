from decouple import config
from django.conf import settings
from django.db.models import Q
from geopy import units, distance
from pyfcm import FCMNotification

from Homes.Houses.models import House, HouseVisit
from Homes.Tenants.models import TenantMoveOutRequest

from utility.logging_utils import sentry_debug_logger
from utility.random_utils import generate_random_code

notify_scout = FCMNotification(api_key=config('FCM_SERVER_KEY')).notify_single_device

UNASSIGNED = 'unassigned'
ASSIGNED = 'assigned'
COMPLETE = 'complete'
CANCELLED = 'cancelled'

ScoutTaskStatusCategories = ((UNASSIGNED, 'Unassigned'),
                             (ASSIGNED, 'Assigned'),
                             (COMPLETE, 'Complete'),
                             (CANCELLED, 'Cancelled'))

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
NEW_PAYMENT_RECEIVED = 'NewPaymentReceived'
NEW_MESSAGE_RECEIVED = 'NewMessageReceived'

TASK_TYPE = 'task_type'
HOUSE_VISIT = 'House Visit'
HOUSE_VISIT_CANCELLED = 'House Visit Cancelled'

MOVE_OUT = 'Move Out'
MOVE_OUT_REMARK = 'Move Out Remark'
MOVE_OUT_AMENITY_CHECKUP = 'Move Out Amenity Checkup'

PROPERTY_ONBOARDING = 'Property Onboarding'
PROPERTY_ONBOARDING_HOUSE_ADDRESS_SUBTASK = 'Property Onboarding House Address Subtask'
PROPERTY_ONBOARDING_HOUSE_PHOTOS_SUBTASK = 'Property Onboarding House Photos Subtask'
PROPERTY_ONBOARDING_HOUSE_AMENITIY_SUBTASK = 'Property Onboarding House Amenity Subtask'
PROPERTY_ONBOARDING_HOUSE_BASIC_DETAILS_SUBTASK = 'Property Onboarding House Basic Details Subtask'


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


def get_nearby_scouts(latitude, longitude, distance_range=50, queryset=None):
    from scouts.models import Scout
    if queryset is None:
        queryset = Scout.objects.all()
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2
    latitude, longitude = float(latitude), float(longitude)
    queryset = queryset.filter(work_address__latitude__range=(latitude - rough_distance, latitude + rough_distance),
                               work_address__longitude__range=(longitude - rough_distance, longitude + rough_distance))
    return queryset


def get_sorted_scouts_nearby(house_latitude, house_longitude, distance_range=50, queryset=None):
    if queryset is None:
        from scouts.models import Scout
        queryset = Scout.objects.all()

    # from scouts.models import Flag
    # if manual control is enabled switch calls by priority
    # flag = Flag.objects.filter(name='MANUAL_CONTROL_FOR_SCOUTS').first()
    # if flag:
    #     if flag.enabled:
    #         sentry_debug_logger.debug("using manual control")
    #         queryset = queryset.order_by('-priority')
    #         result = []
    #         for scout in queryset:
    #             result.append((scout, 0))  # just random distance (0) in result
    #         return result

    queryset = get_nearby_scouts(house_latitude, house_longitude, distance_range, queryset)

    result = []
    for scout in queryset:
        exact_distance = distance.distance((house_latitude, house_longitude), (scout.work_address.latitude,
                                                                               scout.work_address.longitude)).km
        if exact_distance <= distance_range:
            result.append((scout, exact_distance))

    result.sort(key=lambda x: x[1])
    # sentry_debug_logger.debug("sorted scouts are " + str(result))
    return result


def get_appropriate_scout_for_the_task(task, scouts=None):
    from scouts.models import ScoutTaskAssignmentRequest
    from scouts.models import Scout

    house = House.objects.using(settings.HOMES_DB).filter(id=task.house_id).first()

    scheduled_task_time = None

    if task.category.name == HOUSE_VISIT:
        house_visit = HouseVisit.objects.using(settings.HOMES_DB).filter(id=task.visit_id).first()
        scheduled_task_time = house_visit.scheduled_visit_time
        house_latitude = house.address.latitude
        house_longitude = house.address.longitude

    elif task.category.name == MOVE_OUT:
        scheduled_task_time = TenantMoveOutRequest.objects.using(settings.HOMES_DB).filter(id=task.move_out_request_id) \
            .first().timing
        house_latitude = house.address.latitude
        house_longitude = house.address.longitude

    elif task.category.name == PROPERTY_ONBOARDING:
        from scouts.sub_tasks.models import PropertyOnBoardingDetail
        property_on_boarding_detail = PropertyOnBoardingDetail.objects.filter(id=task.onboarding_property_details_id)\
            .first()
        scheduled_task_time = property_on_boarding_detail.scheduled_at
        house_latitude = property_on_boarding_detail.latitude
        house_longitude = property_on_boarding_detail.longitude

    else:
        raise Exception({'detail': 'Task category is not in the choices available'})

    if scouts is None:
        scouts = Scout.objects.all()

    # Remove all those scouts from the task when request is rejected
    rejected_scouts_id = ScoutTaskAssignmentRequest.objects.filter(task=task, status=REQUEST_REJECTED). \
        values_list('scout', flat=True)
    scouts = scouts.exclude(id__in=rejected_scouts_id)

    if scheduled_task_time:
        # filter the scouts whose scheduled availabilities  lie between visit scheduled visit time
        scouts = scouts.filter(Q(scheduled_availabilities__start_time__lte=scheduled_task_time) &
                               Q(scheduled_availabilities__end_time__gte=scheduled_task_time) &
                               Q(scheduled_availabilities__cancelled=False))

    sentry_debug_logger.debug("queryset is " + str(scouts))

    sorted_scouts = get_sorted_scouts_nearby(house_latitude=house_latitude,
                                             house_longitude=house_longitude,
                                             distance_range=50, queryset=scouts)

    try:
        selected_scout = sorted_scouts[0][0]
        if len(sorted_scouts) == 1:
            # CHANGE ALL REQUEST_REJECTED to REQUEST_AWAITED
            ScoutTaskAssignmentRequest.objects.filter(task=task, status=REQUEST_REJECTED, auto_rejected=True).update(
                status=REQUEST_AWAITED,
                auto_rejected=False)

    except Exception as E:
        selected_scout = None

    # sentry_debug_logger.debug("received scout is " + str(selected_scout))

    return selected_scout


SCOUT_PAYMENT_MESSAGE_WALLET = 'Payment for {} on {}'  # credited to your wallet'
SCOUT_PAYMENT_MESSAGE_BANK = 'Payment for {} on {}'  # credited to your bank account and debited from wallet'


def get_description_for_completion_of_current_task_and_receiving_payment_in_wallet(instance):
    global SCOUT_PAYMENT_MESSAGE_WALLET
    return SCOUT_PAYMENT_MESSAGE_WALLET.format(instance.category.name, str(instance.scheduled_at.strftime("%B %d")))


def get_description_for_completion_of_current_task_and_receiving_payment_in_bank_account(instance):
    global SCOUT_PAYMENT_MESSAGE_BANK
    return SCOUT_PAYMENT_MESSAGE_BANK.format(instance.category.name, str(instance.scheduled_at.strftime("%B %d")))
