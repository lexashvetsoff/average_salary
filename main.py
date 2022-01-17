import requests
from terminaltables import AsciiTable
from pprint import pprint

def predict_rub_salary_hh(vacansy):
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


def predict_rub_salary_sj(vacancy):
        if vacancy['currency'] == 'rub':
            if vacancy['payment_from'] != 0 and vacancy['payment_to'] != 0:
                return (vacancy['payment_from'] + vacancy['payment_to']) / 2
            elif vacancy['payment_from'] == 0 and vacancy['payment_to'] != 0:
                return vacancy['payment_to'] * 0.8
            elif vacancy['payment_from'] != 0 and vacancy['payment_to'] == 0:
                return  vacancy['payment_from'] * 1.2
            else:
                return None
        else:
            return None


def get_count_pages(total, count):
    if total % count != 0:
        return (total // count) + 1
    else:
        return total // count


def print_table(data, title, titles):
    table_data = []
    table_data.append(titles)
    
    for item in data:
        row_table = [item, data[item]['vacancies_found'], data[item]['vacancies_processed'], data[item]['average_salary']]
        table_data.append(row_table)

    table = AsciiTable(table_data, title)
    table.justify_columns[4] = 'right'
    print(table.table)


def requests_hh(langs, url):
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

            vacansyes = answer['items']
            full_vacansyes.extend(vacansyes)

        vacancies_processed = 0
        sum = 0

        for vacansy in full_vacansyes:
            if vacansy['salary'] is not None:
                salary = predict_rub_salary_hh(vacansy['salary'])
                if salary is not None:
                    sum = sum + salary
                    vacancies_processed = vacancies_processed + 1

        average_salary = int(sum / vacancies_processed)

        rating[lang] = {"vacancies_found": answer['found'], 
                        'vacancies_processed': vacancies_processed, 
                        'average_salary': average_salary}
    return rating


def requests_sj(langs, url):
    rating = {}

    for lang in langs:
        full_vacansyes = []

        pages = 1
        page = 0
        count = 50
        while page < pages:
            headers = {
                'X-Api-App-Id': 'v3.r.121869903.b04be04a127192d565b8e50e88de28c1d40457f4.dec3f4bbad8bbf19cdc9a2312447cdc52252fb18'
            }

            payload = {
                'keyword': lang,
                'period': 0,
                'town': 'Москва',
                'catalogues': 'Разработка, программирование',
                'page': page,
                'count': count
            }

            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()

            answer = response.json()
            pages = get_count_pages(answer['total'], count)
            page = page + 1

            vacansyes = answer['objects']
            full_vacansyes.extend(vacansyes)

        vacancies_processed = 0
        sum = 0

        for vacansy in full_vacansyes:
            salary = predict_rub_salary_sj(vacansy)
            if salary is not None:
                sum = sum + salary
                vacancies_processed = vacancies_processed + 1

        average_salary = int(sum / vacancies_processed)

        rating[lang] = {"vacancies_found": answer['total'], 
                        'vacancies_processed': vacancies_processed, 
                        'average_salary': average_salary}
    return rating


langs = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go', 'Objective-C']

url_hh = 'https://api.hh.ru/vacancies'
url_sj = 'https://api.superjob.ru/2.0/vacancies/'

rating_hh = requests_hh(langs, url_hh)
rating_sj = requests_sj(langs, url_sj)

title_hh = 'HeadHanter Moscow'
title_sj = 'SuperJob Moscow'
titles = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']

print_table(rating_hh, title_hh, titles)
print_table(rating_sj, title_sj, titles)
