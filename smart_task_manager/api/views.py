from rest_framework import viewsets, permissions
from tasks.models import Task
from tasks.serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(assigned_to=self.request.user)
