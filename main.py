import requests
from pprint import pprint

def predict_rub_salary(vacansy):
    if vacansy is not None:
        if vacansy['currency'] == 'RUR':
            if vacansy['from'] is not None and vacansy['to'] is not None:
                return (vacansy['from'] + vacansy['to']) / 2
            elif vacansy['from'] is None and vacansy['to'] is not None:
                return vacansy['to'] * 0.8
            else:
                return  vacansy['from'] * 1.2
        else:
            return None
    else:
        return None

langs = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go', 'Objective-C']
# langs = ['Python']

url = 'https://api.hh.ru/vacancies'

rating = {}

for lang in langs:
    full_vacansyes = []

    pages = 1
    page = 0
    while page < pages:
        payload = {
            'text': f'Программист {lang}',
            'area': 1,
            'only_with_salary': True,
            'period': 30,
            'per_page': 100,  # количество вакансий на странице
            'page': page
        }

        response = requests.get(url, params=payload)
        response.raise_for_status()

        answer = response.json()
        pages = answer['pages']
        page = page + 1
        # print(answer)

        vacansyes = answer['items']
        # print(type(vacansyes))
        full_vacansyes.extend(vacansyes)

    # print(type(full_vacansyes), '+++')
    print(pages, lang)

    vacancies_processed = 0
    sum = 0

    for vacansy in full_vacansyes:
        # print(predict_rub_salary(vacansy['salary']))
        if vacansy['salary'] is not None:
            salary = predict_rub_salary(vacansy['salary'])
            if salary is not None:
                sum = sum + salary
                vacancies_processed = vacancies_processed + 1

    average_salary = int(sum / vacancies_processed)

    rating[lang] = {"vacancies_found": answer['found'], 
                    'vacancies_processed': vacancies_processed, 
                    'average_salary': average_salary}

pprint(rating)
# pprint(full_vacansyes)
