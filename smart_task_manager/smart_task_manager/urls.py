"""
URL configuration for smart_task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from api.views import TaskViewSet

# API ke liye DRF router
router = routers.DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('admin/', admin.site.urls),         # Django admin panel
    path('', include('tasks.urls')),         # tasks app ke URLs ko root ('/') par mount karo
    path('api/', include(router.urls)),      # API endpoints /api/tasks/ par milenge
    path('api-auth/', include('rest_framework.urls')),  # API login/logout ke liye
    path("accounts/", include("allauth.urls")),  # ✅ google login routes
]

