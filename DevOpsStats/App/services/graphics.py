import datetime
import os
from io import StringIO

import pandas as pd
import matplotlib.pyplot as plt
import requests
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

    top_cities = city_counts.head(10)
    other_cities_count = city_counts.iloc[10:].sum()

    other_series = pd.Series({"Другие": other_cities_count})

    city_counts = pd.concat([top_cities, other_series])

    total_vacancies = len(vacancies)
    city_share = (city_counts / total_vacancies) * 100

    city_share = city_share.sort_values(ascending=False)

    plt.figure(figsize=(12, 8))
    city_share.plot(kind='bar', color='skyblue')
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


def plot_salary_by_city(vacancies):
    courses_dict = parse_course()
    if courses_dict is None:
        print("Не удалось получить курсы валют.")
        return None

    cities = []
    salaries = []

    cis_cities = [
        'Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Нижний Новгород',
        'Казань', 'Челябинск', 'Омск', 'Самара', 'Ростов-на-Дону',
        'Минск', 'Гомель', 'Могилев', 'Витебск', 'Гродно',
        'Алматы', 'Нур-Султан', 'Шымкент', 'Актобе', 'Тараз'
    ]

    for vacancy in vacancies:
        salary_from = vacancy.salary_from
        salary_to = vacancy.salary_to
        salary_currency = vacancy.salary_currency

        if salary_from is None or salary_to is None or salary_currency is None:
            continue

        salary_from_rub = convert_to_rub(salary_from, salary_currency, courses_dict)
        salary_to_rub = convert_to_rub(salary_to, salary_currency, courses_dict)

        if salary_from_rub is not None and salary_to_rub is not None:
            average_salary = (salary_from_rub + salary_to_rub) / 2
            city_name = vacancy.area_name

            if city_name in cis_cities:
                cities.append(city_name)
                salaries.append(average_salary)

    if not cities:
        print("Не удалось обработать вакансии с зарплатами.")
        return None

    df = pd.DataFrame({'city': cities, 'salary': salaries})

    city_salary = df.groupby('city')['salary'].mean().sort_values(ascending=False)

    top_cities = city_salary.head(30)

    plt.figure(figsize=(12, 8))
    top_cities.plot(kind='bar', color='lightblue')
    plt.title('Уровень зарплат по городам СНГ (с учетом валютной конвертации)')
    plt.xlabel('Города')
    plt.ylabel('Средняя зарплата (руб.)')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y')

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'salary_by_city.png')
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()

    return file_path


def check_vacancy_plot(file_name, plot_function, data):
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', file_name)
    if not os.path.exists(file_path):
        return plot_function(data)
    else:
        return f'img/{file_name}'



def parse_course():
    date = datetime.date.today()
    formatted_date = date.strftime('%d/%m/%Y')

    try:
        url = f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={formatted_date}'
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f'ERROR: {e}')
        return None

    xml_data = StringIO(response.text)
    try:
        courses = pd.read_xml(xml_data)
    except ValueError as e:
        print(f'Error parsing XML: {e}')
        return None

    currencies = ['USD', 'EUR', 'KZT', 'BYN', 'RUR']
    courses_dict = {}

    for currency in currencies:
        try:
            value = courses[courses['CharCode'] == currency]['Value'].values[0]
            courses_dict[currency] = float(value.replace(',', '.'))
        except IndexError:
            print(f"Currency {currency} not found.")
            courses_dict[currency] = None

    courses_dict['RUR'] = 1

    return courses_dict


def convert_to_rub(salary, currency, courses_dict):
    if currency not in courses_dict or courses_dict[currency] is None:
        return None
    return float(salary) * courses_dict[currency]