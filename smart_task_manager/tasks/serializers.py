from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Task
        fields = ['id','title','description','assigned_to','due_date','priority','status','created_at']
        read_only_fields = ['created_at','assigned_to']
