from __future__ import absolute_import, unicode_literals

from celery import Celery
from django.conf import settings

from utility.environments import set_settings_module

set_settings_module()

app = Celery('HalanxScout', include=['utility.sms_utils'])

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
