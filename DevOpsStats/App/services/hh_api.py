import re
from datetime import datetime

import requests

def hh_api():
    req = requests.get('https://api.hh.ru/vacancies?per_page=10&professional_role=160&order_by=publication_time&text=devops, development operations')
    data = req.json()
    items = data['items']

    result = []
    for item in items:
        salaries = item.get('salary')
        logos = item['employer']['logo_urls']
        city = item.get('address')
        id_vacancy = item.get('id')
        more_data = requests.get(f'https://api.hh.ru/vacancies/{id_vacancy}').json()
        skills_array = [skill['name'] for skill in more_data['key_skills']]
        html_text = more_data['description']
        description = re.sub(r'<.*?>', '', html_text)

        date_obj = datetime.strptime(item['published_at'], "%Y-%m-%dT%H:%M:%S%z")
        published_date = date_obj.strftime("%d.%m.%Y, %H:%M")

        logo = 'static/img/empty_company.png'
        if logos is not None:
            logo = logos['240']

        if salaries is None:
            salaries = {'from': 'Отсутствует', 'to': 'Отсутствует'}
        else:
            from_salary = salaries.get('from')
            to_salary = salaries.get('to')

            if from_salary is None:
                from_salary = 'Отсутствует'
            if to_salary is None:
                to_salary = 'Отсутствует'

            salaries = {
                'from': from_salary,
                'to': to_salary,
                'currency': salaries.get('currency', 'Не указано'),
            }

        if city is None:
            city = 'Пусто'
        else:
            city = city['city']

        dict_vacancy = {
            'title': item['name'],
            'company': item['employer']['name'],
            'salary': salaries,
            'link': item['alternate_url'],
            'logo': logo,
            'desc': description,
            'city': city,
            'experience': item.get('experience')['name'],
            'skills': skills_array,
            'date': published_date,
        }

        result.append(dict_vacancy)
    return result
