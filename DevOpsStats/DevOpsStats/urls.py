"""
URL configuration for DevOpsStats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path


from App.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home', MainPage.as_view()),
    path('lastvacancies', LastVacancies.as_view()),
    path('generalstats', GeneralStats.as_view()),
    path('skills', Skills.as_view()),
    path('geography', Geography.as_view()),
    path('dynamic', Dynamic.as_view()),
    path('api/professions', GetProfessions.as_view()), # Get all professions 
    path('api/professions/<int:pk>', GetProfessionById.as_view()), # Get profession by id 
    path('api/deleteprofession/<int:pk>', DeleteProfessionById.as_view()), # Delete profession by id 
    path('api/createprofession', CreateProfession.as_view()) # Create profession 
]
