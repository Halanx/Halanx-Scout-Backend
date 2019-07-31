import json

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from decouple import config
from django.conf import settings

from customers.utils import CUSTOMER_NOTIFICATION_FROM_SCOUT_APP, HALANX_HOMES_SCOUTAPI_URL
from scouts.utils import TASK_TYPE

logger = get_task_logger(__name__)


@shared_task
def send_customer_notification(customer_id, title, content, category, payload, notification_data):
    logger.info("Sending notification to customer id {}".format(customer_id))

    from UserBase.models import Customer
    customer = Customer.objects.using(settings.HOMES_DB).filter(id=customer_id).first()

    try:
        data = {
            TASK_TYPE: CUSTOMER_NOTIFICATION_FROM_SCOUT_APP,
            "customer_id": customer.id,
            "notification_data": notification_data,
            "notification_payload": payload,
            "category": category
        }

        x = requests.post(HALANX_HOMES_SCOUTAPI_URL, data=json.dumps(data),
                          headers={'Content-type': 'application/json'},
                          timeout=10,
                          auth=(
                          config('HOMES_ADMIN_USERNAME'), config('HOMES_ADMIN_PASSWORD')))

        if x.status_code != 200:
            logger.error("while processing ScoutAPI" + str(x.content))

    except Exception as e:
        logger.error(e)

    logger.info("Sent notification to customer id {}".format(customer_id))


@shared_task
def scout_assignment_request_set_rejected(instance_id):
    from utility.logging_utils import sentry_debug_logger
    try:
        from scouts.models import ScoutTaskAssignmentRequest
        from scouts.utils import REQUEST_AWAITED, REQUEST_REJECTED

        scout_task_assign_request = ScoutTaskAssignmentRequest.objects.filter(id=instance_id).first()
        # Auto Reject a task after 2 minutes
        if scout_task_assign_request:
            if scout_task_assign_request.status == REQUEST_AWAITED:
                scout_task_assign_request.status = REQUEST_REJECTED
                scout_task_assign_request.auto_rejected = True
                scout_task_assign_request.save()
                # sentry_debug_logger.debug("rejected after two minutes" + str(instance_id), exc_info=True)

    except Exception as E:
        sentry_debug_logger.error("execption occured while setting rejected is " + str(E), exc_info=True)
