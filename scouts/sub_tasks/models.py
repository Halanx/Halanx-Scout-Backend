from django.db import models
from rest_framework.fields import JSONField

from scouts.models import ScoutTask, ScoutTaskCategory, ScoutSubTaskCategory
from scouts.utils import MOVE_OUT


#  MOVE OUT SUB TASKS

class MoveOutSubTask(models.Model):
    parent_task_category = models.ForeignKey(ScoutTaskCategory, on_delete=models.SET_NULL, to_field='name',
                                             default=MOVE_OUT, null=True)
    parent_subtask_category = models.ForeignKey(ScoutSubTaskCategory, on_delete=models.SET_NULL, null=True, blank=True)


class MoveOutAmenitiesCheckup(MoveOutSubTask):
    amenities_json = JSONField()
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='move_out_amenity_checkup')


class MoveOutRemark(MoveOutSubTask):
    content = models.TextField(blank=True, null=True)
    task = models.OneToOneField(ScoutTask, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='move_out_remark')
