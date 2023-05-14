import requests
from bs4 import BeautifulSoup as BS
import sqlite3 as sql

url = 'https://www.olx.ua/d/uk/list/q-Квартиры/?page=1'


count = 2

while count <= 500:
    url = 'https://www.olx.ua/d/uk/list/q-Квартиры/?page=' + str(count)
    

    r = requests.get(url)
    soup = BS(r.text, 'lxml')

    name = soup.find_all('h6', class_='css-16v5mdi er34gjf0')
    price = soup.find_all('p', class_='css-10b0gli er34gjf0')


# New Table

    conn = sql.connect('parser.db')
    cursor = conn.cursor()

    createSQL = '''CREATE TABLE IF NOT EXISTS test(name TEXT, price INT, link TEXT)'''
    cursor.execute(createSQL)

    SQL = '''INSERT INTO test (name, price, link) VALUES (?, ?, ?)'''

    for el, name_element, price_element in zip(soup.find_all('a', class_='css-rc5s2u'), name, price):
        link = 'https://www.olx.ua' + el.get('href')
        item_name = name_element.text
        item_price = price_element.text

        cursor.execute(SQL, [item_name, item_price, link])
        conn.commit()
    count += 1
