import json

from celery import shared_task
from celery.utils.log import get_task_logger

from scouts.utils import notify_scout

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
