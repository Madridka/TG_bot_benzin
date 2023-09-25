import os

import telebot
from telebot import types
import sqlite3
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('API_key'))


@bot.message_handler(commands=['start'])
def start(message):
    # создание кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('/start')
    button2 = types.KeyboardButton('Удалить запись')
    button3 = types.KeyboardButton('Таблица')
    button4 = types.KeyboardButton('Заправка')
    markup.row(button1)
    markup.row(button2, button3)
    markup.row(button4)

    # создание таблицы
    db = sqlite3.connect('benzin_bot.sql')
    cur = db.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS benzin ('
                'id INTEGER PRIMARY KEY,'
                'day INT,'
                'Probeg INT,'
                'Raschod FLOAT)')
    db.commit()
    db.close()

    bot.send_message(message.chat.id, 'Привет. Что делаем?', reply_markup=markup)


@bot.message_handler(regexp='Заправка')
def start(message):
    bot.register_next_step_handler(message, day_benz)
    bot.send_message(message.chat.id, f'Дата заправки:')


def day_benz(message):
    global day
    day = message.text.strip()
    bot.send_message(message.chat.id, f'Текущий пробег:')
    bot.register_next_step_handler(message, now_probeg)


def now_probeg(message):
    try:
        global now_prob
        now_prob = int(message.text.strip())
        bot.send_message(message.chat.id, f'Прошлый пробег:')
        bot.register_next_step_handler(message, last_probeg)
    except ValueError:
        bot.send_message(message.chat.id, f'Должно быть число')
        bot.register_next_step_handler(message, now_probeg)


def last_probeg(message):
    try:
        last_prob = int(message.text.strip())
        global probeg
        probeg = int(now_prob) - int(last_prob)
        bot.send_message(message.chat.id, f'Сумма заправки:')
        bot.register_next_step_handler(message, summa)
    except ValueError:
        bot.send_message(message.chat.id, f'Должно быть число')
        bot.register_next_step_handler(message, last_probeg)


def summa(message):
    try:
        global stoim
        stoim = float(message.text.strip())
        bot.send_message(message.chat.id, f'Стоимость бенза:')
        bot.register_next_step_handler(message, price_benzin)
    except ValueError:
        bot.send_message(message.chat.id, f'Должно быть число')
        bot.register_next_step_handler(message, summa)


def price_benzin(message):
    try:
        global price
        price = float(message.text.strip())
        calc(message)
    except ValueError:
        bot.send_message(message.chat.id, f'Число в формате с точкой:')
        bot.register_next_step_handler(message, price_benzin)


def calc(message):
    raschod = round((stoim/price) / (probeg / 100), 1)

    db = sqlite3.connect('benzin_bot.sql')
    cur = db.cursor()

    cur.execute('INSERT into benzin (day, Probeg, Raschod) VALUES ("%s", "%s", "%s")' % (day, probeg, raschod))
    db.commit()
    db.close()
    # show_table(message)
    bot.send_message(message.chat.id, 'Запись добавлена в таблицу')


@bot.message_handler()
def starter(message):
    quest = message.text.strip()
    if quest == 'Удалить запись' or quest == 'удалить':
        show_table(message)
        bot.send_message(message.chat.id, f'Какую запись (id) удалить?')
        bot.register_next_step_handler(message, delete)
    elif quest == 'print' or quest == 'Таблица':
        show_table(message)


def show_table(message):
    try:
        db = sqlite3.connect('benzin_bot.sql')
        cur = db.cursor()
        info = ''
        for value in cur.execute('SELECT id, day, probeg, raschod from benzin'):
            info += f'{value[0]}. Дата: {value[1]}, Пробег: {value[2]}км, Расход: {value[3]}л\n'

        bot.send_message(message.chat.id, info)
    except telebot.apihelper.ApiTelegramException:
        bot.send_message(message.chat.id, 'Таблица пуста')


def delete(message):
    what_id = message.text.strip()

    db = sqlite3.connect('benzin_bot.sql')
    cur = db.cursor()

    cur.execute(f'DELETE FROM benzin WHERE id = {what_id}')
    db.commit()
    db.close()

    bot.send_message(message.chat.id, f'Удалена запись № {what_id}')
    show_table(message)


# @bot.callback_query_handler(func=lambda call: True)
# def callback(call):
#     db = sqlite3.connect('benzin_bot.sql')
#     cur = db.cursor()
#     cur.execute('SELECT * from benzin')
#     benz = cur.fetchall()
#
#     info = ''
#     for value in benz:
#         info += f'id: {value[0]}, Дата: {value[1]}, Пробег: {value[2]}км, Расход: {value[3]}л/100км\n'
#
#     cur.close()
#     db.close()
#
#     bot.send_message(call.message.chat.id, info)

bot.polling(none_stop=True)
