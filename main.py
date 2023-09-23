import telebot
from telebot import types
import sqlite3 as sl
import json

con = sl.connect('delivery_db.db')
bot = telebot.TeleBot('6312431700:AAEea6F81xq0uO28q-dKs6Q8WCfZBvYMioY')

bot_description = """
Привет! Я - Ваш помощник-бот. Моя задача - помогать Вам с доставкой еды.
Здесь Вы можете найти следующие возможности:
- "Начать" - Запуск основного функционала;
- "Отзывы" - Узнайте мнение других пользователей о боте;
- "О боте" - Получить информацию обо мне.
"""


@bot.message_handler(commands=['start'])
def start_handler(message):
    send_main_menu_inline(message)

@bot.message_handler(commands=['admin'])
def admin_command(message):
    bot.send_message(message.chat.id,'Админ панель/ В разработке...')

def send_main_menu_inline(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать', callback_data='begin'))
    keyboard.add(types.InlineKeyboardButton('Отзывы', callback_data='reviews'))
    keyboard.add(types.InlineKeyboardButton('О боте', callback_data='about_bot'))
    bot.send_message(message.chat.id, text='Выберите действие:', reply_markup=keyboard)


def user_exists(user_id):
    con = sl.connect('delivery_db.db')
    with con:
        result = con.execute("SELECT name FROM users WHERE user_id = ?", (user_id,)).fetchone()
    con.close()
    return result


def add_user(user_id, username, phone=None, address=None):
    con = sl.connect('delivery_db.db')
    with con:
        con.execute("INSERT INTO users (user_id, name, phone, address) VALUES (?, ?, ?, ?);",
                    (user_id, username, phone, address))
        con.commit()
    con.close()


def update_user(user_id, phone=None, address=None):
    con = sl.connect('delivery_db.db')
    with con:
        if phone:
            con.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        if address:
            con.execute("UPDATE users SET address = ? WHERE user_id = ?", (address, user_id))
        con.commit()
    con.close()


def request_phone_number(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите ваш номер телефона:")


@bot.message_handler(func=lambda message: user_exists(message.chat.id))
def process_input(message):
    if message.text.startswith("+"):
        handle_phone_number(message)
    else:
        process_address(message)

# Пока адрес временно , Пока не сделаем необходимые окна
def handle_phone_number(message):
    phone_number = message.text
    user_id = message.chat.id

    user_info = user_exists(user_id)
    if user_info:
        update_user(user_id, phone=phone_number)
        bot.send_message(message.chat.id, "Пожалуйста, введите ваш адрес:")
    else:
        bot.send_message(message.chat.id, "Ошибка! Пользователь не найден в базе данных.")


def process_address(message):
    address = message.text
    user_id = message.chat.id

    user_info = user_exists(user_id)
    if user_info:
        update_user(user_id, address=address)
        bot.send_message(message.chat.id, f"Адрес успешно добавлен: {address}")
    else:
        bot.send_message(message.chat.id, "Ошибка! Пользователь не найден в базе данных.")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == "begin":
        user_id = call.message.chat.id
        username = call.message.chat.username

        if not user_exists(user_id):
            add_user(user_id, username)
            request_phone_number(call.message)
        else:
            bot.send_message(chat_id=user_id, text=f"Добро пожаловать, {username}!")
    elif call.data == 'reviews':
        # Обработка кнопки "Отзывы"
        pass
    elif call.data == 'about_bot':
        bot.send_message(call.message.chat.id, text=bot_description)



bot.infinity_polling()
