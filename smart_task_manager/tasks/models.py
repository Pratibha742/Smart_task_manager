from django.db import models
from django.contrib.auth.models import User
from .utils import ai_suggest_priority

class Task(models.Model):
    PRIORITY_CHOICES = [('Low','Low'),('Medium','Medium'),('High','High')]
    STATUS_CHOICES = [('Pending','Pending'),('In Progress','In Progress'),('On hold','On hold')]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # ✅ Status-based priority override
        if self.status == "On hold":
            self.priority = "Low"
        elif self.status == "Pending":
            # AI / due_date logic
            suggestion = ai_suggest_priority(f"{self.title} {self.description}", self.due_date)
            if suggestion in ["Low", "Medium", "High"]:
                self.priority = suggestion
            else:
                self.priority = "Medium"
        elif self.status == "In Progress":
            # 👇 Yahan tum decide kar sakti ho
            # Example: due date based priority allow
            suggestion = ai_suggest_priority(f"{self.title} {self.description}", self.due_date)
            self.priority = suggestion if suggestion in ["Low","Medium","High"] else "Medium"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.priority})"
    
    

