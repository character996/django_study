"""djangotest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from polls import views
from .settings import DEBUG

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.show_subjects),
    path('login/', views.login),
    path('logout/', views.logout),
    path('teachers/', views.show_teachers),
    path('praise/', views.praise_or_criticize),
    path('criticize/', views.praise_or_criticize),
    path('captcha/', views.get_captcha),
    path('excel/', views.export_teachers_excel),
    path('teachers_data/', views.get_teachers_data),
    path('register/', views.register),
    path('teacher_data_show/', views.teacher_data_show),
    path('api/subjects/', views.show_subjects_api),
    path('subjects_show/', views.subjects_show)
]
if DEBUG:

    import debug_toolbar

    urlpatterns.insert(0, path('__debug__/', include(debug_toolbar.urls)))
