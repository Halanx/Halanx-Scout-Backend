from rest_framework import serializers

from scouts.sub_tasks.models import MoveOutRemark


class MoveOutRemarkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoveOutRemark
        exclude = ('task', 'parent_subtask', 'sub_task')

