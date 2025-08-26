from django.core.management.base import BaseCommand
from tasks.notifications import send_due_task_notifications

class Command(BaseCommand):
    help="Send Email Reminders For Tasks Due Soon"

    def handle(self, *args, **kwargs):
        send_due_task_notifications()
        self.stdout.write(self.style.SUCCESS("✅ Task reminders sent successfully"))