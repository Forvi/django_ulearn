import os

from django.shortcuts import render
from django.views import View

from .models import Profession
from .services.graphics import *
from .services.hh_api import hh_api
from DevOpsStats import settings


class MainPage(View):
    def get(self, request):
        return render(request, 'main.html')


class GeneralStats(View):
    def get(self, request):
        vacancies = Profession.objects.all()

        data = {
            'published_at': [vacancy.published_at for vacancy in vacancies],
        }

        file_path_year = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'vacancies_by_year.png')
        if os.path.exists(file_path_year) is False:
            vacancies_per_year = plot_vacancies_per_year(data)
        else:
            vacancies_per_year = 'img/vacancies_by_year.png'

        file_path_top = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'top20.png')
        if os.path.exists(file_path_top) is False:
            vacancies_top20 = plot_top_vacancies_per_year(vacancies)
        else:
            vacancies_top20 = 'img/top20.png'

        vacancies_by_city = ''
        file_path_top = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'vacancies_by_city.png')
        if os.path.exists(file_path_top) is False:
            vacancies_by_city = plot_vacancies_by_city(vacancies)
        else:
            vacancies_by_city = 'img/vacancies_by_city.png'


        context = {
            'vacancies': vacancies,
            'plot_vacancies_per_year': vacancies_per_year,
            'vacancies_top20': vacancies_top20,
            'vacancies_by_year': vacancies_by_city,
        }
        return render(request, 'generalstats.html', context)


class LastVacancies(View):
    def get(self, request):
        items = hh_api()

        context = {
            'items': items,
        }
        return render(request, 'LastVacancies.html', context)

