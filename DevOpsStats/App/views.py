from django.shortcuts import redirect, render
from django.views import View

from App.serializers import *
from .models import Profession
from .services.graphics import *
from .services.hh_api import hh_api

from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import *
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from .serializers import UserSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework import status


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
        return render(request, 'lastvacancies.html', context)


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
    


# _______________   REST METHODS _____________

class ProfessionAPIView(APIView): 
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk=None):
        if pk is not None:
            try:
                professions = Profession.objects.get(pk=pk)
                serializer = ProfessionSerializer(professions)
                return Response({'professions': serializer.data}, status=200)
            except Profession.DoesNotExist:
                return Response({'error': 'not found'}, status=404) 
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
    
    def delete(self, request, pk=None):
        if pk is not None:
            try:
                profession = Profession.objects.get(pk=pk) 
                profession.delete() 
                return Response({'message': 'profession deleted'}, status=204)
            except Profession.DoesNotExist:
                return Response({'error': 'not found'}, status=404)
            except ValidationError as e:
                return Response({'error': str(e)}, status=400)


# __________ Auth _______________

# class RegisterView(generics.CreateAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = UserSerializer
#     # renderer_classes = [TemplateHTMLRenderer, JSONRenderer]


# class LoginView(APIView):
#     permission_classes = [AllowAny]
#     renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

#     def get(self, request):
#         return Response({'template_name': 'login.html'}, template_name='login.html')
    
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
#             if user:
#                 token, created = Token.objects.get_or_create(user=user)
                
#                 # Возвращаем токен в формате JSON
#                 return Response({
#                     'token': token.key,
#                     'redirect_url': '/skills/'  # Можно вернуть URL для перенаправления, если нужно
#                 }, status=status.HTTP_200_OK)

#             return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class Skills(APIView):
#     renderer_classes = [TemplateHTMLRenderer, JSONRenderer]

#     def get(self, request):
#         token = request.session.get('')
#         vacancies = Profession.objects.all()
#         vacancies_top20 = check_vacancy_plot('top20.png', plot_top_vacancies_per_year, vacancies)
#         return Response({'vacancies': vacancies_top20}, template_name='skills.html')