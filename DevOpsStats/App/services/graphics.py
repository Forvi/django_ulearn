import os
import pandas as pd
import matplotlib.pyplot as plt
from django.conf import settings


def plot_vacancies_per_year(data):
    df = pd.DataFrame(data)

    df['published_at'] = pd.to_datetime(df['published_at'])
    df['year'] = df['published_at'].dt.year

    vacancies_per_year = df['year'].value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    index = vacancies_per_year.index
    values = vacancies_per_year.values
    plt.bar(index, values, color='skyblue')
    plt.title('Динамика количества вакансий по годам')
    plt.xlabel('Год')
    plt.ylabel('Количество вакансий')
    plt.xticks(index)
    plt.grid(axis='y')

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'vacancies_by_year.png')

    plt.savefig(file_path)
    plt.close()

    return 'img/vacancies_by_year.png'


def plot_top_vacancies_per_year(vacancies):
    skills = []
    for vacancy in vacancies:
        skills.extend(vacancy.key_skills.split())

    skill_counts = pd.Series(skills).value_counts().nlargest(20)

    plt.figure(figsize=(10, 6))
    skill_counts.plot(kind='bar', color='skyblue')
    plt.title('ТОП-20 навыков по количеству вакансий')
    plt.xlabel('Навыки')
    plt.ylabel('Количество вакансий')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'top20.png')
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path


def plot_vacancies_by_city(vacancies):
    cities = [vacancy.area_name for vacancy in vacancies]
    city_counts = pd.Series(cities).value_counts()

    total_vacancies = len(vacancies)
    city_share = (city_counts / total_vacancies) * 100  # Доля в процентах

    # Сортировка по убыванию
    city_share = city_share.sort_values(ascending=False)

    # Построение графика
    plt.figure(figsize=(12, 8))
    city_share.plot(kind='bar', color='lightblue')
    plt.title('Доля вакансий по городам')
    plt.xlabel('Города')
    plt.ylabel('Доля вакансий (%)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'vacancies_by_city.png')
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    return file_path

