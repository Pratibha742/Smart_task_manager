from django.urls import path
from django.shortcuts import redirect
from . import views
from django.contrib.auth import views as auth_views

def redirect_signup(request):
    return redirect('/accounts/signup/')

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('tasks/', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('login/', auth_views.LoginView.as_view(template_name='tasks/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'), 
    path('run-task/<str:token>/',views.trigger_notifications,name='run-task')

]