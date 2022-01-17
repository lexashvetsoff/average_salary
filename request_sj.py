import requests
from terminaltables import AsciiTable
from pprint import pprint


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


langs = ['JavaScript', 'Java', 'Python', 'Ruby', 'PHP', 'C++', 'C#', 'C', 'Go', 'Objective-C']

url = '	https://api.superjob.ru/2.0/vacancies/'

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
            # 'keywords': ['and', 'программист python'],
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

    print(pages, lang)

    vacancies_processed = 0
    sum = 0

    for vacansy in full_vacansyes:
        # print(predict_rub_salary(vacansy['salary']))
        salary = predict_rub_salary_sj(vacansy)
        if salary is not None:
            sum = sum + salary
            vacancies_processed = vacancies_processed + 1

    average_salary = int(sum / vacancies_processed)

    rating[lang] = {"vacancies_found": answer['total'], 
                    'vacancies_processed': vacancies_processed, 
                    'average_salary': average_salary}

# pprint(rating)
# print(answer)
title = 'SuperJob Moscow'
titles = ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата']

print_table(rating, title, titles)