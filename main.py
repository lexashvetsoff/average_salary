import requests
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def predict_rub_salary(vacansy, payment_from, paymen_to):
    if vacansy['currency'] == 'rub':
        if payment_from and paymen_to:
            return (payment_from + paymen_to) / 2
        elif not payment_from and paymen_to:
            return paymen_to * 0.8
        elif payment_from and not paymen_to:
            return  payment_from * 1.2
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
        lang = data[item]
        row_table = [item, lang['vacancies_found'], lang['vacancies_processed'], lang['average_salary']]
        table_data.append(row_table)

    table = AsciiTable(table_data, title)
    table.justify_columns[4] = 'right'
    print(table.table)


def get_average_salary_hh(vacancies):
    vacancies_processed = 0
    sum = 0

    for vacansy in vacancies:
        if vacansy['salary']:
            hh_vacansy = vacansy['salary']
            salary = predict_rub_salary(hh_vacansy, hh_vacansy['from'], hh_vacansy['to'])
            if salary:
                sum = sum + salary
                vacancies_processed += 1
    
    average = int(sum / vacancies_processed)

    return average, vacancies_processed


def get_avarage_salary_sj(vacancies):
    vacancies_processed = 0
    sum = 0

    for vacansy in vacancies:
        salary = predict_rub_salary(vacansy, vacansy['payment_from'], vacansy['payment_to'])
        if salary:
            sum = sum + salary
            vacancies_processed += 1

    average = int(sum / vacancies_processed)

    return average, vacancies_processed


def make_requests_hh(langs, url):
    rating = {}

    for lang in langs:
        full_vacancies = []

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
            page += 1

            vacansyes = answer['items']
            full_vacancies.extend(vacansyes)

        average_salary, vacancies_processed = get_average_salary_hh

        rating[lang] = {"vacancies_found": answer['found'], 
                        'vacancies_processed': vacancies_processed, 
                        'average_salary': average_salary}
    return rating


def make_requests_sj(langs, url, secret_key):
    rating = {}

    for lang in langs:
        full_vacancies = []

        pages = 1
        page = 0
        count = 50
        while page < pages:
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
            page += 1

            vacansyes = answer['objects']
            full_vacancies.extend(vacansyes)

        average_salary, vacancies_processed = get_avarage_salary_sj(full_vacancies)

        rating[lang] = {"vacancies_found": answer['total'], 
                        'vacancies_processed': vacancies_processed, 
                        'average_salary': average_salary}
    return rating


def main():
    load_dotenv()

    secret_key = os.getenv('SECRET_KEY_SJ')
    langs = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go', 'Objective-C']

    url_hh = 'https://api.hh.ru/vacancies'
    url_sj = 'https://api.superjob.ru/2.0/vacancies/'

    rating_hh = make_requests_hh(langs, url_hh)
    rating_sj = make_requests_sj(langs, url_sj, secret_key)

    title_hh = 'HeadHanter Moscow'
    title_sj = 'SuperJob Moscow'
    titles = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']

    print_table(rating_hh, title_hh, titles)
    print_table(rating_sj, title_sj, titles)


if __name__ == '__main__':
    main()
