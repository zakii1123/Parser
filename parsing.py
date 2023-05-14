


import requests
from bs4 import BeautifulSoup as BS
import sqlite3 as sql

url = 'https://www.olx.ua/d/uk/list/q-Квартиры/?page=1'


houses = list()

count = 2

while count <= 100:
    url = 'https://www.olx.ua/d/uk/list/q-Квартиры/?page=' + str(count)
    

    r = requests.get(url)
    soup = BS(r.text, 'lxml')

    name = soup.find_all('h6', class_='css-16v5mdi er34gjf0')
    price = soup.find_all('p', class_='css-10b0gli er34gjf0')






# Сбор всех ссылок 
    for el in soup.find_all('a', class_='css-rc5s2u'):
        link = ('https://www.olx.ua' + el.get('href'))
    # print (link.split()) # Если пригодиться в будущем
    # print(link)


# New Table

    conn = sql.connect('parser.db')
    cursor = conn.cursor()

    createSQL = '''CREATE TABLE IF NOT EXISTS test(name TEXT, price INT, link TEXT)'''
    cursor.execute(createSQL)

    SQL = '''INSERT INTO test (name, price, link) VALUES (?, ?, ?)'''



    for i in range(len(price)):
        item_name = name[i].text
        item_price = price[i].text
    
        cursor.execute(SQL, [item_name, item_price, link])
        conn.commit()

    count += 1






