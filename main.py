import requests
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv
from itertools import count


def predict_rub_salary(vacansy, payment_from, paymen_to):
    if vacansy['currency'] != 'rub':
        return None
    if payment_from and paymen_to:
        return (payment_from + paymen_to) / 2
    elif paymen_to:
        return paymen_to * 0.8
    elif payment_from:
        return payment_from * 1.2


def get_count_pages(total, count):
    if total % count:
        return (total // count) + 1
    else:
        return total // count


def create_table(data, title):
    titles = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
    ]
    table_data = []
    table_data.append(titles)

    for item in data:
        lang = data[item]
        row_table = [
            item,
            lang['vacancies_found'],
            lang['vacancies_processed'],
            lang['average_salary']
        ]
        table_data.append(row_table)

    table = AsciiTable(table_data, title)
    table.justify_columns[4] = 'right'
    return table.table


def get_salary_avarage_hh(vacancies, answer):
    vacancies_processed = 0
    salary_sum = 0

    for vacansy in vacancies:
        if vacansy['salary']:
            hh_vacansy = vacansy['salary']
            salary = predict_rub_salary(hh_vacansy,
                                        hh_vacansy['from'],
                                        hh_vacansy['to'])
            if salary:
                salary_sum += salary
                vacancies_processed += 1

    average = int(salary_sum / vacancies_processed)

    rating = {"vacancies_found": answer['found'],
                        'vacancies_processed': vacancies_processed,
                        'average_salary': average}

    return rating


def get_salary_avarage_sj(vacancies, answer):
    vacancies_processed = 0
    salary_sum = 0

    for vacansy in vacancies:
        salary = predict_rub_salary(vacansy,
                                    vacansy['payment_from'],
                                    vacansy['payment_to'])
        if salary:
            salary_sum += salary
            vacancies_processed += 1

    average = int(salary_sum / vacancies_processed)

    rating = {"vacancies_found": answer['total'],
             'vacancies_processed': vacancies_processed,
             'average_salary': average}

    return rating


def get_vacancies_hh(lang):
    full_vacancies = []
    url = 'https://api.hh.ru/vacancies'

    for page in count(start=0, step=1):    
        payload = {
            'text': f'Программист {lang}',
            'area': 1,   # город Москва
            'period': 30,
            'per_page': 100,  # количество вакансий на странице
            'page': page
        }

        response = requests.get(url, params=payload)
        response.raise_for_status()

        answer = response.json()
        pages = answer['pages']

        vacancies = answer['items']
        full_vacancies.extend(vacancies)

        if page >= pages:
            break

    return answer, full_vacancies


def get_vacancies_sj(lang, secret_key):
    full_vacancies = []
    url = 'https://api.superjob.ru/2.0/vacancies/'

    count = 50
    for page in count(start=0, step=1):    
        headers = {
            'X-Api-App-Id': secret_key
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

        vacancies = answer['objects']
        full_vacancies.extend(vacancies)

        if page >= pages:
            break
    
    return answer, full_vacancies


def get_statistics_hh(langs):
    rating = {}

    for lang in langs:
        answer, full_vacancies = get_vacancies_hh(lang)
        rating[lang] = get_salary_avarage_hh(full_vacancies, answer)
    return rating


def get_statistics_sj(langs, secret_key):
    rating = {}

    for lang in langs:
        answer, full_vacancies = get_vacancies_sj(lang, secret_key)
        rating[lang] = get_salary_avarage_sj(full_vacancies, answer)
    return rating


def main():
    load_dotenv()

    secret_key = os.getenv('SECRET_KEY_SJ')
    langs = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Objective-C'
    ]

    rating_hh = get_statistics_hh(langs)
    rating_sj = get_statistics_sj(langs, secret_key)

    title_hh = 'HeadHanter Moscow'
    title_sj = 'SuperJob Moscow'

    print(create_table(rating_hh, title_hh))
    print(create_table(rating_sj, title_sj))


if __name__ == '__main__':
    main()
