import datetime
import os.path
import random
import re
import time

import requests
import bs4
import json
import csv
from time import sleep


def get_page(url: str, payload=None, pause=0):
    if payload is None:
        payload = {}
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 "
                      "Safari/537.36",
        "Accept": "*/*"
    }
    r = requests.get(url=url, headers=headers, params=payload)
    sleep(pause)
    return r.text


def save2json(data, filename):
    if not os.path.exists("json"):
        os.mkdir('./json')

    with open(f'json/{filename}.json', 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def save2file(data, filename):
    if not os.path.exists("files"):
        os.mkdir('files')

    path = filename.split('/')[0]
    if not os.path.exists(f"files/{path}"):
        os.mkdir(f'files/{path}')

    with open(f'files/{filename}', 'w') as file:
        file.write(data)
        file.close()


def save2csv(data, filename):
    if not os.path.exists("CSV"):
        os.mkdir('CSV')

    with open(f'CSV/{filename}.csv', 'a', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)


def get_products_link():
    # записал все ссылки в файл
    link_to_product = []
    for page in range(1, 4):
        url = f'https://www.etm.ru/brand/138_dkc?page={page}&rows=40'
        r = get_page(url)
        product_links = r.find_all('div', attrs={'data-testid': re.compile('catalog-item-product')})
        for link in product_links:
            out_url = 'https://www.etm.ru' + link.find('a').get('href').strip()
            link_to_product.append(out_url)
    with open(f'./files/links.txt', 'a') as file:
        for line in link_to_product:
            file.write(f'{line}\n')
    with open('./files/products/101.html') as file:
        q = bs4.BeautifulSoup(file, 'lxml')
        res = q.find(text=re.compile('Производитель:')).parent.find_all('span')[-1].text
        print(res)


def collect_data():
    # прохожусь по ссылкам из файла
    start_time = time.time()
    with open('./files/links.txt') as file:
        lines = [line.strip() for line in file.readlines()]
        max_line = len(lines)
        count = 1
        titles = ('Бренд', 'Артикул', 'Наименование', 'Категория (конечная)')
        save2csv(titles, 'product_2')
        for line in lines:
            pause = random.randint(3, 5)
            if count % 5:
                pause = pause + 2
            q = get_page(line, pause=pause)
            result = bs4.BeautifulSoup(q, 'lxml')
            try:
                product_category = result.find_all(class_='jss109')[-1].text.strip()
                product_title = result.find('h1').text.strip()
                product_brand = result.find(text=re.compile('Производитель:')).parent.find_all('span')[-1].text.strip()
                product_articulate = result.find(text=re.compile('Артикул:')).parent.find_all('span')[-1].text.strip()

            except Exception:
                # Если данные не получены, повторить через 10 секунд
                print('No connect. Wait 10s and try again')
                sleep(10)
                pause = pause + 10
                print(f'try again request to\t{line}')
                q = get_page(line, pause=pause)
                result = bs4.BeautifulSoup(q, 'lxml')

                product_category = result.find_all(class_='jss109')[-1].text.strip()
                product_title = result.find('h1').text.strip()
                product_brand = result.find(text=re.compile('Производитель:')).parent.find_all('span')[-1].text.strip()
                product_articulate = result.find(text=re.compile('Артикул:')).parent.find_all('span')[-1].text.strip()

            prod_data = (
                product_brand,
                product_articulate,
                product_title,
                product_category
            )
            save2csv(prod_data, 'product_2')
            print(f'[INFO] Сохранено товаров: {count}/{max_line}\t '
                  f'Задержка: {pause}')
            count = count + 1

    out = time.time() - start_time
    sec = int(out % 60)
    minute = int(out // 60)
    hour = int(minute // 60)
    print(f'[INFO] Затрачено времени: {hour}:{minute}:{sec}\n'
          f'[INFO] RAW: {out}')


def collect_data_json():
    # Можно было вытянуть почти все данные через json, но там не было данных о конечной категории.
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 "
                      "Safari/537.36",
        "Accept": "*/*"
    }
    page = 1
    url = f'https://www.etm.ru/_next/data/O90Sgt0HKDoXmqmPt8djT/catalog.json?conf=mnf%24432%7C&page={page}&rows=20'
    req = requests.get(url, headers=headers)
    print(req.text)
    save2json(req.json(), 'list')


def main():
    collect_data()


if __name__ == '__main__':
    main()
