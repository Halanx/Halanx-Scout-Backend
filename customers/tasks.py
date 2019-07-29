import json

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

logger = get_task_logger(__name__)


@shared_task
def send_customer_notification(customer_id, title, content, category, payload):
    logger.info("Sending notification to customer id {}".format(customer_id))

    from UserBase.models import Customer
    customer = Customer.objects.using(settings.HOMES_DB).filter(id=customer_id).first()

    try:
        from customers.utils import notify_customer
        notify_customer(registration_id=customer.gcm_id,
                        data_message={'data': json.dumps({'title': title, 'content': content,
                                                          'category': category, 'payload': payload})})
    except Exception as e:
        logger.error(e)

    logger.info("Sent notification to customer id {}".format(customer_id))


@shared_task
def scout_assignment_request_set_rejected(instance_id):
    try:
        from utility.logging_utils import sentry_debug_logger
        from scouts.models import ScoutTaskAssignmentRequest
        from scouts.utils import REQUEST_AWAITED, REQUEST_REJECTED

        scout_task_assign_request = ScoutTaskAssignmentRequest.objects.filter(id=instance_id).first()
        # Auto Reject a task after 2 minutes
        if scout_task_assign_request:
            if scout_task_assign_request.status == REQUEST_AWAITED:
                scout_task_assign_request.status = REQUEST_REJECTED
                scout_task_assign_request.auto_rejected = True
                scout_task_assign_request.save()
                sentry_debug_logger.debug("rejected after two minutes" + str(instance_id), exc_info=True)

    except Exception as E:
        sentry_debug_logger.error("execption occured is " + str(E), exc_info=True)
