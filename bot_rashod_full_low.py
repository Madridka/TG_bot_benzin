import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('5801104246:AAEkk5G_u5ZJ3H5YACC5Ocso84UxlpZfdTo')
storage = {}

def init_storage(user_id):
  storage[user_id] = dict()

def store_number(user_id, key, value):
  storage[user_id][key] = dict(value=value)

def get_number(user_id, key):
  return storage[user_id][key].get('value')

@bot.message_handler(commands=['start'])
def start (message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/start')
    markup.add(item1)

    conn = sqlite3.connect('rashod.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS rashod ('
                'id int primary key, '
                'day varchar(50),'
                'prp float,'
                'tp float,'
                'summa float,'
                'rashod float)')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Дата заправки', reply_markup=markup)
    bot.register_next_step_handler(message, day)

def day(message):
    init_storage(message.from_user.id)
    global day_benz
    day_benz = message.text.strip()
    bot.send_message(message.chat.id, 'Предыдущий пробег')
    bot.register_next_step_handler(message, prp)

def prp(message):
    global prp_benz
    prp_benz = message.text.strip()
    store_number(message.from_user.id, 'prp', prp_benz)
    bot.send_message(message.chat.id, 'Текущий пробег')
    bot.register_next_step_handler(message, tp)

def tp(message):
    global tp_benz
    tp_benz = message.text.strip()
    store_number(message.from_user.id, 'tp', tp_benz)
    bot.send_message(message.chat.id, 'Сумма')
    bot.register_next_step_handler(message, summa)

def summa(message):
    global summa_benz
    summa_benz = message.text.strip()
    store_number(message.from_user.id, 'summa', summa_benz)

    n1 = float(get_number(message.from_user.id, 'prp'))
    n2 = float(get_number(message.from_user.id, 'tp'))
    n3 = float(get_number(message.from_user.id, 'summa'))

    rash = round((n3/ 47.75) / ((n2-n1)/100),1)
    bot.send_message(message.chat.id, f'Расход: {rash} л./ 100км')

    conn = sqlite3.connect('rashod.sql')
    cur = conn.cursor()

    cur.execute('INSERT into rashod (day, prp, tp, summa, rashod) VALUES ("%s", "%s", "%s", "%s", "%s")' % (day_benz, prp_benz, tp_benz, summa_benz, rash))
    conn.commit()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Общая таблица', callback_data='rashod'))
    bot.send_message(message.chat.id, 'Все посчитано. Таблица ниже.', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('rashod.sql')
    cur = conn.cursor()

    cur.execute('SELECT * from rashod')
    users = cur.fetchall()

    info = ''
    for el in users:
        info += f'Дата заправки: {el[1]}, Расход: {el[5]} л. / 100 км\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)




bot.polling(none_stop=True)