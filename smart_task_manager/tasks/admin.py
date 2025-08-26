from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title','assigned_to','priority','status','due_date','created_at')
    list_filter = ('priority','status','assigned_to')
    search_fields = ('title','description','assigned_to__username')


# Register your models here.
