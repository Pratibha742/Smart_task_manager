from django.core.mail import send_mail
from django.conf import settings
from datetime import date
from .models import Task


def send_due_task_notifications():
    tasks = Task.objects.filter(due_date__gte=date.today())
    for task in tasks:
        days_left =(task.due_date - date.today()).days
        if days_left <= 2:  # send reminder
            if days_left <= 2:
                send_mail(
                    "⏰ Task Reminder",
                    f"Hi {task.assigned_to.username},\n\nYour task '{task.title}' is due on {task.due_date}. Please complete it soon!",
                    settings.DEFAULT_FROM_EMAIL,
                    [task.assigned_to.email],
                    fail_silently=False,  # better: show errors if any
            )