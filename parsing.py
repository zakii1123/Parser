#Парсер сайта OLX по 3-м категориям: Недвижимость, транспорт, гаджеты и т.д.
#Даниил Чумаков
#
#Импорт библиотек

import sys
import requests
from bs4 import BeautifulSoup as BS
import sqlite3 as sql
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel



#Образец парсера для всех категорий

class ParserThread(QThread):
    finished = pyqtSignal() #Хз, с инета скатал

    def __init__(self, url):
        super().__init__()
        self.url = url  

    def run(self):
        conn = sql.connect('parser.db') #Коннект к Базе данных
        cursor = conn.cursor()
        createSQL = '''CREATE TABLE IF NOT EXISTS test(name TEXT, price INT, link TEXT)'''   #Создание таблицы SQL
        cursor.execute(createSQL)
        conn.commit()

        count = 2
        run = True
        
        #Сам парсер
        while run == True:
            url = self.url + str(count)

            r = requests.get(url)
            soup = BS(r.text, 'lxml')

            name = soup.find_all('h6', class_='css-16v5mdi er34gjf0')
            price = soup.find_all('p', class_='css-10b0gli er34gjf0')
            

            SQL = '''INSERT INTO test (name, price, link) VALUES (?, ?, ?)'''

            for el, name_element, price_element in zip(soup.find_all('a', class_='css-rc5s2u'), name, price):
                link = 'https://www.olx.ua' + el.get('href')
                item_name = name_element.text
                item_price = price_element.text
                print(item_name)
                cursor.execute(SQL, [item_name, item_price, link])
                conn.commit()
            count += 1

        cursor.close()
        conn.close()
        self.finished.emit()


#Интерфейс

class FunctionSelector(QWidget):
    def __init__(self):
        super().__init__()

        self.current_function = None   #Выбранная кнопка

        self.setWindowTitle('Function Selector')  #название окна

        main_layout = QVBoxLayout() #Основная линия на которой лежать виджеты

        self.label = QLabel('Select a function:')  
        main_layout.addWidget(self.label)

        self.function_buttons = []

        self.function_buttons.append(QPushButton('Недвижимость'))       #|
        self.function_buttons.append(QPushButton('Транспорт'))          # - Кнопки Категорий
        self.function_buttons.append(QPushButton('Электроника'))        #|

        for button in self.function_buttons:  #Цикл для проверки все кнопок 
            button.clicked.connect(self.on_function_button_clicked)   #Проверяет нажата ли кнопка
            main_layout.addWidget(button)  #Ложим виджет на воображаемую линию

        button_layout = QHBoxLayout()  #2 линия для доп. кнопок (start/stop)
        self.start_button = QPushButton('Start')
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.on_stop_button_clicked)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)  #Ложим линию с доп.кнопками на основную линию

        self.setLayout(main_layout)  

        self.parser_thread = None   #Забыл как называется, но она помогает нам оброщаться к пэрэнт Классу

        self.conn = sql.connect('parser.db')   #Дэфолт подключение к базе данных, уже как родной
        self.cursor = self.conn.cursor()
        self.createSQL = '''CREATE TABLE IF NOT EXISTS test(name TEXT, price INT, link TEXT)'''
        self.cursor.execute(self.createSQL)
        self.conn.commit()
#
#Функции
#

    #Функция проверяет выбрана ли категория и дает возможность запустить парсер
    def on_function_button_clicked(self):
        sender = self.sender()
        self.current_function = sender.text()
        self.label.setText(f'Selected function: {self.current_function}')
        print(f'Selected function: {self.current_function}')
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    
    
    #Распределяет функции
    def on_start_button_clicked(self):
        if self.current_function == 'Недвижимость':
            self.start_parser_1()
        elif self.current_function == 'Транспорт':
            self.start_parser_2()

        elif self.current_function == 'Электроника':
            self.start_parser_3()

        self.start_button.setEnabled(False) #Блокаирует кнопку старт и активирует кнопку стоп
        self.stop_button.setEnabled(True)
    #Функция остановки парсера
    def on_stop_button_clicked(self):
        if self.parser_thread:
            self.parser_thread.terminate()
            self.parser_thread.wait()
            self.parser_thread = None

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
    #Парсер категории Недвижимость
    def start_parser_1(self):
        self.parser_thread = ParserThread('https://www.olx.ua/d/uk/nedvizhimost/?page=')
        self.parser_thread.finished.connect(self.on_parser_finished)
        self.parser_thread.start()
    #Парсер категории транспорт
    def start_parser_2(self):
        self.parser_thread = ParserThread('https://www.olx.ua/d/uk/transport/?page=')
        self.parser_thread.finished.connect(self.on_parser_finished)
        self.parser_thread.start()
    #Парсер категории электроника 
    def start_parser_3(self):
        self.parser_thread = ParserThread('https://www.olx.ua/d/uk/elektronika/?page=')
        self.parser_thread.finished.connect(self.on_parser_finished)
        self.parser_thread.start()

    #Обработчик событий (завершин поток парсинга или нет)
    def on_parser_finished(self):
        self.parser_thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    #Завершает все события и делает безопасный выход из приложения
    def closeEvent(self, event):
        if self.parser_thread:
            self.parser_thread.terminate()
            self.parser_thread.wait()

        self.cursor.close()
        self.conn.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = FunctionSelector()
    selector.show()
    sys.exit(app.exec_())
