from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import Task
from .forms import TaskForm
from datetime import date, timedelta
from django.db.models import Q
from .utils import ai_suggest_priority
from django.utils.timezone import localdate
from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

def welcome(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    return render(request, 'tasks/welcome.html')

# @login_required
# def task_list(request):
#     today = localdate()
#     soon = today + timedelta(days=2)
#     tasks =(Task.objects.filter(assigned_to=request.user).select_related('assigned_to'))

#     urgent_tasks = tasks.filter(
#     status__in=['pending', 'in progress'],
#     due_date__lte=date.today() + timedelta(days=2)
# ).filter(
#     Q(priority="High") | Q(due_date__lte=date.today() + timedelta(days=2))
# )
#     return render(request, 'tasks/task_list.html', {'tasks': tasks,'urgent_tasks':urgent_tasks})

@login_required
def task_list(request):
    today = localdate()
    soon = today + timedelta(days=2)

    tasks = Task.objects.filter(assigned_to=request.user).select_related('assigned_to')

    # Urgent = High priority + due within 2 days + still not finished
    urgent_tasks = tasks.filter(
        priority="High",
        status__in=['pending', 'in progress'],
        due_date__lte=soon
    )

    return render(
        request,
        'tasks/task_list.html',
        {
            'tasks': tasks,
            'urgent_tasks': urgent_tasks
        }
    )

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_to = request.user

            # 🔥 AI hamesha priority decide karega
            suggestion = ai_suggest_priority(f"{task.title} {task.description}",task.due_date)
            if suggestion in ['Low', 'Medium', 'High']:
                task.priority = suggestion
            else:
                task.priority = "Medium"  # default fallback

            task.save()
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form})


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ✅ user ko authenticate karo taaki backend set ho jaye
            authenticated_user = authenticate(
                request,
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"]
            )

            if authenticated_user is not None:
                login(request, authenticated_user)  # backend ab set hoga
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tasks/sign_up.html', {'form': form})


def trigger_notifications(request, token):
    if token != settings.CRON_SECRET:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    try:
        call_command("send_task_reminder")   # ye tumhari management command ko run karega
        return JsonResponse({"status": "success", "message": "notifications triggered"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
@login_required
def delete_task(request, task_id):
    if request.method == "POST":
        try:
            task = Task.objects.get(id=task_id, assigned_to=request.user)
            task.delete()
            return JsonResponse({"status":"success"})
        except Task.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Task not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)

def send_reminder_now(request):
    today = localdate()
    soon = today + timedelta(days=2)
    
      # STEP 1: Update Medium/Low tasks -> High, if due_date within 2 days
    Task.objects.filter(
        Q(priority="Medium") | Q(priority="Low"),
        due_date__lte=soon
    ).update(priority="High")

     # High priority tasks jo jaldi due hain
    tasks= Task.objects.filter(
        priority ="High", 
        due_date__lte = soon,
        status="Pending",           # 🟢 Completed skip ho jayenge
        assigned_to=request.user )
    
    if tasks.exists():
        subject = "High Priority Task Reminder"
        message = "These high priorities tasks are pending\n\n"
        for task in tasks:
            message += f"- {task.title} (Due: {task.due_date})\n"
            recipient = [request.user.email]
            
            send_mail(
            subject,
            message,
            "noreply@yourapp.com",  # from email
            recipient,
            fail_silently=False,
        )
        messages.success(request, "Reminder email sent successfully!")
    else:
        messages.warning(request, "No high priority tasks found to remind.")

    return redirect("task_list")  # ya jis page pe tum dikhana chahte ho

def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("task_list")  # list page pe redirect
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form})