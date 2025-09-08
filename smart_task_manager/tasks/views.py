from django.shortcuts import render,redirect
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


def welcome(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    return render(request, 'tasks/welcome.html')

@login_required
def task_list(request):
    today = localdate()
    soon = today + timedelta(days=2)
    tasks =(Task.objects.filter(assigned_to=request.user).select_related('assigned_to'))

    urgent_tasks = tasks.filter(
    status__in=['pending', 'in progress'],
    due_date__lte=date.today() + timedelta(days=2)
).filter(
    Q(priority="High") | Q(due_date__lte=date.today() + timedelta(days=2))
)
    return render(request, 'tasks/task_list.html', {'tasks': tasks,'urgent_tasks':urgent_tasks})

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




def trigger_notifications(request,token):
    if token != settings.CRON_SECRET:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)

    call_command = ("send_task_notifications")
    return JsonResponse({"status": "success" ,"message":"notifications triggered"})