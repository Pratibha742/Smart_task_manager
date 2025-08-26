from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .models import Task
from .forms import TaskForm
from datetime import date, timedelta
from django.db.models import Q
from .utils import ai_suggest_priority

@login_required
def task_list(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    urgent_tasks = tasks.filter(
        Q(due_date__lte=date.today() + timedelta(days=2)) | Q(priority="High")
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
            user = form.save(commit=False)  # naya user save karega
            user.email = form.cleaned_data["email"]
            user.save()
            login(request, user)  # auto login ke baad
            return redirect('task_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tasks/sign_up.html', {'form': form})
