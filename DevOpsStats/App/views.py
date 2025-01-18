import os
from django.http import HttpResponse
from django.utils import timezone

from django.shortcuts import render
from django.views import View

from App.serializers import ProfessionSerializer

from .models import Profession
from .services.graphics import *
from .services.hh_api import hh_api
from DevOpsStats import settings
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


class MainPage(View):
    def get(self, request):
        return render(request, 'main.html')


class GeneralStats(View):
    def get(self, request):
        vacancies = Profession.objects.all()
        data = {
            'published_at': [vacancy.published_at for vacancy in vacancies],
        }

        vacancies_per_year = check_vacancy_plot('vacancies_by_year.png', plot_vacancies_per_year, data)
        vacancies_top20 = check_vacancy_plot('top20.png', plot_top_vacancies_per_year, vacancies)
        vacancies_by_city = check_vacancy_plot('vacancies_by_city.png', plot_vacancies_by_city, vacancies)
        vacancies_salary_by_city = check_vacancy_plot('salary_by_city.png', plot_salary_by_city, vacancies)

        context = {
            'vacancies': vacancies,
            'plot_vacancies_per_year': vacancies_per_year,
            'vacancies_top20': vacancies_top20,
            'vacancies_by_year': vacancies_by_city,
            'vacancies_salary_by_city': vacancies_salary_by_city,
        }

        return render(request, 'generalstats.html', context)


class LastVacancies(View):
    def get(self, request):
        items = hh_api()

        context = {
            'items': items,
        }
        return render(request, 'LastVacancies.html', context)


class Skills(View):
    def get(self, request):
        vacancies = Profession.objects.all()
        vacancies_top20 = check_vacancy_plot('top20.png', plot_top_vacancies_per_year, vacancies)
        
        context = {
            'vacancies_top20': vacancies_top20,
        }

        return render(request, 'skills.html', context)
    

class Geography(View):
    def get(self, request):
        vacancies = Profession.objects.all()

        vacancies_salary_by_city = check_vacancy_plot('salary_by_city.png', plot_salary_by_city, vacancies)
        vacancies_by_city = check_vacancy_plot('vacancies_by_city.png', plot_vacancies_by_city, vacancies)

        
        context = {
            'vacancies_by_year': vacancies_by_city,
            'vacancies_salary_by_city': vacancies_salary_by_city,
        }

        return render(request, 'geography.html', context)


class Dynamic(View):
    def get(self, request):
        vacancies = Profession.objects.all()
        vacancies_by_city = check_vacancy_plot('vacancies_by_city.png', plot_vacancies_by_city, vacancies)
       
        context = {
            'vacancies_by_year': vacancies_by_city,
        }

        return render(request, 'dynamic.html', context)
    


# _______________ CRUD METHODS _____________


# class GetProfessions(generics.ListAPIView):
#     queryset = Profession.objects.all()
#     serializer_class = ProfessionSerializer


# class GetProfessionById(generics.RetrieveAPIView):
#     queryset = Profession.objects.all()
#     serializer_class = ProfessionSerializer


# class DeleteProfessionById(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Profession.objects.all()
#     serializer_class = ProfessionSerializer


# class CreateProfession(generics.CreateAPIView):
#     queryset = Profession.objects.all()
#     serializer_class = ProfessionSerializer

#     def perform_create(self, serializer):
#         serializer.save(published_at=timezone.now())


class ProfessionAPIView(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            try:
                professions = Profession.objects.get(pk=pk)
                serializer = ProfessionSerializer(professions)
                return Response({'professions': serializer.data}, status=200)
            except ValidationError as e:
                return Response({str(e)}, status=400)

        try:
            professions = Profession.objects.all()
            serializer = ProfessionSerializer(professions, many=True)
            return Response({'professions': serializer.data}, status=200)
        except ValidationError as e:
            return Response({str(e)}, status=400)

    def post(self, request):
        try:
            serializer = ProfessionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)  
            serializer.save()
            return Response({'post': serializer.data}, status=201)  
        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'error': 'PK not found'}, status=400)
        
        try:
            instance = Profession.objects.get(pk=pk)
        except Profession.DoesNotExist:
            return Response({'error': 'Profession not found'}, status=404)
        
        serializer = ProfessionSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True) 
        serializer.save()
        return Response({'profession': serializer.data})
