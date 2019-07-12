import json

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def send_scout_notification(scout_id, title, content, category, payload):
    logger.info("Sending notification to scout id {}".format(scout_id))

    from scouts.models import Scout
    scout = Scout.objects.get(id=scout_id)

    try:
        notify_scout(registration_id=scout.gcm_id,
                     data_message={'data': json.dumps({'title': title, 'content': content,
                                                       'category': category, 'payload': payload})})
    except Exception as e:
        logger.error(e)

    logger.info("Sent notification to scout id {}".format(scout_id))


@shared_task
def scout_assignment_request_set_rejected(instance_id):
    from utility.logging_utils import sentry_debug_logger
    from scouts.models import ScoutTaskAssignmentRequest
    from scouts.utils import REQUEST_AWAITED

    sentry_debug_logger.debug("sending it after 2 minutes with data" + str(instance_id), exc_info=True)
    scout_task_assign_request = ScoutTaskAssignmentRequest.objects.get(id=instance_id)
    if scout_task_assign_request.status == REQUEST_AWAITED:
        from scouts.utils import REQUEST_REJECTED
        scout_task_assign_request.status = REQUEST_REJECTED
        scout_task_assign_request.save()
