import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import json
from tabulate import tabulate
from keyboardsDelivery import send_main_menu_inline, send_admin_keyboard, send_manager_keyboard,inline_keyboard_admin_bd, admin_menu_keyboard


global con

con = sl.connect('delivery_db.db')

bot = telebot.TeleBot('6312431700:AAEea6F81xq0uO28q-dKs6Q8WCfZBvYMioY')


bot_description = """
Привет! Я - Ваш помощник-бот. Моя задача - помогать Вам с доставкой еды.
Здесь Вы можете найти следующие возможности:
- "Начать" - Запуск основного функционала;
- "Отзывы" - Узнайте мнение других пользователей о боте;
- "О боте" - Получить информацию обо мне.
"""
user_states = {}
STATE_AWAITING_PHONE = 1
STATE_AWAITING_ADDRESS = 2

input_id = 1
user_name = ''
user_phone = ''
product_name = ''
product_description = ''
header_list = []
header_users = ['name', 'phone','address']
header_products = ['name', 'description', 'price', 'amount', 'rating']
update_id = 1
update_value = ''




@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, text='Выберите действие:', reply_markup=send_main_menu_inline())



def request_admin_credentials(message):
    msg = bot.send_message(message.chat.id, "Введите ваш логин:")
    bot.register_next_step_handler(msg, process_admin_login)


def process_admin_login(message):
    login = message.text
    msg = bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(msg, lambda message: process_admin_password(message, login))


def process_admin_password(message, login):
    password = message.text
    user = check_admin_credentials(login, password)
    if user:
        if user[2] == 'admin':
            keyboard = send_admin_keyboard()
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)
        elif user[2] == 'manager':
            keyboard = send_manager_keyboard()
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Неверные учетные данные. Пожалуйста, попробуйте еще раз.")



@bot.message_handler(commands=['admin'])
def admin_command(message):
    request_admin_credentials(message)


def check_admin_credentials(login, password):
    with con:
        result_admin = con.execute("SELECT * FROM admins WHERE login = ? AND password = ?", (login, password)).fetchone()
        result_manager = con.execute("SELECT * FROM managers WHERE login = ? AND password = ?", (login, password)).fetchone()
    con.close()

    if result_admin:
        return result_admin[0], result_admin[1], 'admin'
    elif result_manager:
        return result_manager[0], result_manager[1], 'manager'

    return None


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
    user_states[message.chat.id] = STATE_AWAITING_PHONE
    bot.send_message(message.chat.id, "Пожалуйста, введите ваш номер телефона:")



@bot.message_handler(func=lambda message: user_exists(message.chat.id) and message.chat.id in user_states)
def process_input(message):
    state = user_states[message.chat.id]
    if state == STATE_AWAITING_PHONE and message.text.startswith("+"):
        handle_phone_number(message)
    elif state == STATE_AWAITING_ADDRESS:
        process_address(message)
    else:
        # Если состояние отсутствует или неправильное,  либо проигнорировать сообщение или отправить ответ пользователю
        bot.send_message(message.chat.id, "Непонятное сообщение. Пожалуйста, следуйте инструкциям.")



def handle_phone_number(message):
    phone_number = message.text
    user_id = message.chat.id

    user_info = user_exists(user_id)
    if user_info:
        update_user(user_id, phone=phone_number)
        user_states[user_id] = STATE_AWAITING_ADDRESS
        bot.send_message(message.chat.id, "Пожалуйста, введите ваш адрес:")
    else:
        bot.send_message(message.chat.id, "Ошибка! Пользователь не найден в базе данных.")

def process_address(message):
    address = message.text
    user_id = message.chat.id

    user_info = user_exists(user_id)
    if user_info:
        update_user(user_id, address=address)
        user_states.pop(user_id)  # Удаляем состояние пользователя
        bot.send_message(message.chat.id, f"Адрес успешно добавлен: {address}")
    else:
        bot.send_message(message.chat.id, "Ошибка! Пользователь не найден в базе данных.")


def send_categories_keyboard(message):
    keyboard = types.InlineKeyboardMarkup()
    con = sl.connect('delivery_db.db')
    with con:
        categories = con.execute("SELECT * FROM categories").fetchall()

    for category in categories:
        keyboard.add(types.InlineKeyboardButton(category[1], callback_data=f"category_{category[0]}"))

    bot.send_message(message.chat.id, text='Выберите категорию:', reply_markup=keyboard)


user_states = {}
user_messages = {}  # Для сохранения списка сообщений с блюдами для каждого пользователя

def send_dishes_by_category(message, category_id):
    user_id = message.chat.id
    con = sl.connect('delivery_db.db')
    with con:
        dishes = con.execute("SELECT * FROM products WHERE category_id = ?", (category_id,)).fetchall()

    messages_to_delete = []  # Сохраняет весь список message_id с блюдами
    for dish in dishes:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton('Добавить в корзину', callback_data=f"add_to_cart_{dish[0]}"),
            types.InlineKeyboardButton('Перейти в корзину', callback_data='goto_cart')
        )

        dish_text = f"Название: {dish[1]}\nОписание: {dish[2]}\nЦена: {dish[3]} руб\nРейтинг: {dish[5]}"
        sent_message = bot.send_message(chat_id=message.chat.id, text=dish_text, reply_markup=keyboard)
        messages_to_delete.append(sent_message.message_id)

    user_messages[user_id] = messages_to_delete  # Сохраняет список message_id для каждого пользователя

    keyboard_back = types.InlineKeyboardMarkup()
    keyboard_back.add(types.InlineKeyboardButton("Назад", callback_data="back_to_categories"))
    back_message = bot.send_message(chat_id=message.chat.id, text="Нажмите 'Назад', чтобы вернуться к категориям", reply_markup=keyboard_back)
    user_messages[user_id].append(back_message.message_id)  # Сохраняет message_id сообщения с кнопкой "Назад"


def show_cart(message, edit=False):
    user_id = message.chat.id
    con = sl.connect('delivery_db.db')
    with con:
        cart_items = con.execute("""
            SELECT p.product_id, p.name, p.price, c.amount
            FROM cart c
            JOIN products p ON p.product_id = c.product_id
            WHERE c.user_id = ?""",
                                 (user_id,)).fetchall()

    if len(cart_items) == 0:
        bot.send_message(chat_id=user_id, text="Ваша корзина пуста!")
        return

    total_cost = 0
    for item in cart_items:
        dish_text = f"{item[1]} x {item[3]} = {item[2] * item[3]} руб"
        total_cost += item[2] * item[3]

        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("Добавить еще", callback_data=f"add_more_cart_{item[0]}"),
            types.InlineKeyboardButton("Убрать", callback_data=f"remove_one_cart_{item[0]}"),
        )
        keyboard.row(types.InlineKeyboardButton("Удалить все", callback_data=f"remove_all_cart_{item[0]}"))

        if edit:
            bot.edit_message_text(chat_id=user_id, message_id=message.message_id, text=dish_text, reply_markup=keyboard)
        else:
            bot.send_message(chat_id=user_id, text=dish_text, reply_markup=keyboard)

    bot.send_message(chat_id=user_id, text=f"Итого: {total_cost} руб")


def update_cart_items(call, action_type):
    user_id = call.message.chat.id
    product_id = int(call.data.split("_")[-1])

    con = sl.connect('delivery_db.db')

    with con:
        item_in_cart = con.execute("SELECT amount FROM cart WHERE user_id = ? AND product_id = ?",
                                   (user_id, product_id)).fetchone()
        if item_in_cart:
            if action_type == "add_more":
                con.execute("UPDATE cart SET amount = amount + 1 WHERE user_id = ? AND product_id = ?",
                            (user_id, product_id))
            elif action_type == "remove_one" and item_in_cart[0] > 1:
                con.execute("UPDATE cart SET amount = amount - 1 WHERE user_id = ? AND product_id = ?",
                            (user_id, product_id))
            elif action_type == "remove_one" and item_in_cart[0] == 1:
                con.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            elif action_type == "remove_all":
                con.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))

            con.commit()

            show_cart(call.message, edit=True)
        else:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text="Этот товар отсутствует в корзине!")


user_last_add_message = {}  # Для сохранения последнего сообщения с добавлением товара в корзину для каждого пользователя

def add_product_to_cart(message, product_id):
    user_id = message.chat.id

    con = sl.connect('delivery_db.db')

    with con:
        product_name = con.execute("SELECT name FROM products WHERE user_id = ?", (product_id,)).fetchone()[
            0]  # Получаем название продукта

        existing_product = con.execute("SELECT amount FROM cart WHERE user_id = ? AND product_id = ?",
                                       (user_id, product_id)).fetchone()

        if existing_product:
            con.execute("UPDATE cart SET amount = amount + 1 WHERE user_id = ? AND product_id = ?",
                        (user_id, product_id))
        else:
            con.execute("INSERT INTO cart (user_id, product_id, amount) VALUES (?, ?, ?)", (user_id, product_id, 1))

        con.commit()

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Добавить еще', callback_data=f"add_more_{product_id}"),
        types.InlineKeyboardButton('Убрать', callback_data=f"remove_one_{product_id}")
    )

    # Удаляем предыдущее сообщение с добавлением товара, если оно существует
    if user_id in user_last_add_message:
        last_add_message_id = user_last_add_message[user_id]
        bot.delete_message(chat_id=user_id, message_id=last_add_message_id)

    # Отправляем новое сообщение и сохраняем его message_id
    sent_message = bot.send_message(chat_id=message.chat.id, text=f"Товар {product_name} успешно добавлен в корзину!",
                                    reply_markup=keyboard)
    user_last_add_message[user_id] = sent_message.message_id



def remove_product_from_cart(message, product_id):
    user_id = message.chat.id
    con = sl.connect('delivery_db.db')
    with con:
        existing_product = con.execute("SELECT amount FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id)).fetchone()

        if existing_product and existing_product[0] > 1:
            con.execute("UPDATE cart SET amount = amount - 1 WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        elif existing_product and existing_product[0] == 1:
            con.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        else:
            bot.send_message(chat_id=message.chat.id, text="Товар отсутствует в корзине!")
            return

        con.commit()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Добавить еще', callback_data=f"add_more_{product_id}"),
        types.InlineKeyboardButton('Убрать', callback_data=f"remove_one_{product_id}")
    )
    bot.send_message(chat_id=message.chat.id, text="Успешно обновлено количество товара в корзине!", reply_markup=keyboard)



def users_id(message, data):
    global user_id_manual
    user_id_manual = message.text
    try:
        user_id_manual = int(user_id_manual)
    except ValueError:
        pass

    bot.send_message(message.chat.id, "Внесите номер телефона")
    bot.register_next_step_handler(message, users_phone, data)


def users_address(message, data):
    con = sl.connect('delivery_db.db')
    global user_address
    user_address = message.text
    keyboard3 = types.InlineKeyboardMarkup()
    keyboard3.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
    keyboard3.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
    with con:
        con.execute("""INSERT INTO users values (?, ?, ?, ?)""", (user_id_manual,user_name, user_phone, user_address))
    bot.send_message(message.chat.id, f"""Данные добавлены в таблицу {data}""", reply_markup=keyboard3)

# Функция принимает id строки, которую нужно удалить из таблицы
def delete(message, data):
    con = sl.connect('delivery_db.db')
    # print(data)
    id_list = []
    global input_id
    input_id = message.text
    try:
        input_id = int(input_id)
    except ValueError:
        pass
    with con:
        id_exist = con.execute(f"""SELECT user_id FROM {data} """)
        id_exist = (id_exist.fetchall())
        for i in id_exist:
            id_list.append(i[0])
        # print(id_list)
    if input_id in id_list:
        keyboard1 = types.InlineKeyboardMarkup()
        keyboard1.add(types.InlineKeyboardButton('Удалить', callback_data=f'd{data}'))
        keyboard1.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
        keyboard1.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
        bot.send_message(message.chat.id, text='Что делаем дальше c данными?', reply_markup=keyboard1)
    else:
        bot.send_message(message.chat.id, text='Нет такого id')
        keyboard8 = types.InlineKeyboardMarkup()
        keyboard8.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
        keyboard8.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
        bot.send_message(message.chat.id, text='Что делаем дальше?', reply_markup=keyboard8)


# Функция принимает имя пользователя и просит ввести номер телефона
def users_name(message, data):
    global user_name
    user_name = message.text

    bot.send_message(message.chat.id, "Внесите user_id:")
    bot.register_next_step_handler(message, users_id, data)



# Функция принимает номер телефона пользователя и добавляет строку в таблицу
def users_phone(message, data):
    con = sl.connect('delivery_db.db')
    global user_id_manual, user_phone
    user_phone = message.text

    keyboard3 = types.InlineKeyboardMarkup()
    keyboard3.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
    keyboard3.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))

    bot.send_message(message.chat.id, "Введите адрес пользователя:")
    bot.register_next_step_handler(message, users_address, data)

# Функция принимает название продукта и просит добавить описание
def products_name(message, data):
    global product_name
    product_name = message.text
    bot.send_message(message.chat.id, "Добавьте описание продукта")
    bot.register_next_step_handler(message, products_description, data)


def products_description(message, data):
    global product_description
    product_description = message.text
    bot.send_message(message.chat.id, "Цена, руб.")
    bot.register_next_step_handler(message, products_price, data)


def products_price(message, data):
    global product_price
    product_price = message.text
    bot.send_message(message.chat.id, "Количество в остатке, шт.")
    bot.register_next_step_handler(message, products_amount, data)


def products_amount(message, data):
    global product_amount
    product_amount = message.text
    bot.send_message(message.chat.id, "Рейтинг")
    bot.register_next_step_handler(message, products_rating, data)


def products_rating(message, data):
    global product_rating
    product_rating = message.text
    bot.send_message(message.chat.id, "Введите category_id:")
    bot.register_next_step_handler(message, products_category_id, data)


def products_category_id(message, data):
    con = sl.connect('delivery_db.db')
    global product_category_id
    product_category_id = message.text
    try:
        product_category_id = int(product_category_id)
    except ValueError:
        pass

    if not category_id_exists(product_category_id):
        bot.send_message(message.chat.id, "Введенный category_id не существует в таблице categories. Пожалуйста, введите корректный.")
        bot.register_next_step_handler(message, products_category_id, data)
        return

    keyboard4 = types.InlineKeyboardMarkup()
    keyboard4.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
    keyboard4.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))

    with con:
        con.execute("""INSERT INTO products (name, description, price, amount, rating, category_id) values (?, ?, ?, ?, ?, ?)""",
                    (product_name, product_description, product_price, product_amount, product_rating, product_category_id))
    bot.send_message(message.chat.id, f"Данные добавлены в таблицу {data}", reply_markup=keyboard4)


# Функция предлагает набор кнопок, полей таблицы, после указания строки для редактирования
def update_buttons(message, data):
    con = sl.connect('delivery_db.db')
    global update_id
    global header_list
    update_id = message.text
    update_id_list = []
    # print(data)
    if data == 'users':
        header_list = header_users
        # print(header_list)
    if data == 'products':
        header_list = header_products + ['category_id']
    try:
        update_id = int(update_id)
    except ValueError:
        pass
    with con:
        update_id_exist = con.execute(f"""SELECT user_id FROM {data} """)
        update_id_exist = (update_id_exist.fetchall())
        for i in update_id_exist:
            update_id_list.append(i[0])
        # print(update_id_list)
    if update_id in update_id_list:
        keyboard5 = types.InlineKeyboardMarkup()
        for i in header_list:
            keyboard5.add(types.InlineKeyboardButton(i, callback_data=f'p{data}.{i}'))
            # print(i)
        bot.send_message(message.chat.id, f"Выберите поле таблицы {data} и редактируйте его", reply_markup=keyboard5)
    else:
        bot.send_message(message.chat.id, text='Нет такого id')
        keyboard9 = types.InlineKeyboardMarkup()
        keyboard9.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
        keyboard9.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
        bot.send_message(message.chat.id, text='Что делаем дальше?', reply_markup=keyboard9)

def category_id_exists(category_id):
    con = sl.connect('delivery_db.db')
    with con:
        existed_category_ids = con.execute("SELECT category_id FROM categories")
        existed_category_ids = [item[0] for item in existed_category_ids.fetchall()]
    return category_id in existed_category_ids


# Функция принимает изменённое значение поля
def update_field(message, data, field):
    con = sl.connect('delivery_db.db')
    global update_value
    update_value = message.text

    if field == 'category_id':
        try:
            update_value = int(update_value)
        except ValueError:
            bot.send_message(message.chat.id, 'Неверное значение для category_id, введите число')
            bot.register_next_step_handler(message, update_field, data, field)
            return

        if not category_id_exists(update_value):
            bot.send_message(message.chat.id, "Введенный category_id не существует в таблице categories. Пожалуйста, введите корректный.")
            bot.register_next_step_handler(message, update_field, data, field)
            return

    keyboard6 = types.InlineKeyboardMarkup()
    keyboard6.add(types.InlineKeyboardButton('Подтвердить изменение', callback_data=f'c{data}.{field}'))
    keyboard6.add(types.InlineKeyboardButton(f'Вернуться в таблицу {data}', callback_data=f's{data}'))
    keyboard6.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
    bot.send_message(message.chat.id, f"Изменить значение поля {field} в таблице {data} с "
                                      f"id {update_id} на {update_value}?", reply_markup=keyboard6)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(callback_query_id=call.id)
    user_id = call.message.chat.id
    data = call.data[1:]
    flag = call.data[0]

    if call.data == "begin":
        user_id = call.message.chat.id
        username = call.message.chat.username

        if not user_exists(user_id):
            add_user(user_id, username)
            request_phone_number(call.message)
        else:
            bot.send_message(chat_id=user_id, text=f"Добро пожаловать, {username}!")
            send_categories_keyboard(call.message)
    elif call.data == 'reviews':
        # Обработка кнопки "Отзывы"
        pass
    elif call.data == 'about_bot':
        bot.send_message(call.message.chat.id, text=bot_description)
    elif call.data.startswith("category_"):
        category_id = int(call.data.split("_")[-1])
        bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.message_id)  # Удаление сообщения с категориями
        send_dishes_by_category(call.message, category_id)
    elif call.data == "back_to_categories":
        user_id = call.message.chat.id
        if user_id in user_messages:
            for msg_id in user_messages[user_id]:
                bot.delete_message(chat_id=user_id, message_id=msg_id)
            user_messages.pop(user_id)  # Удаляем сохраненные сообщения пользователя
        send_categories_keyboard(call.message)
    elif call.data.startswith("add_to_cart_"):
        product_id = int(call.data.split("_")[-1])
        add_product_to_cart(call.message, product_id)
    elif call.data.startswith("add_more_"):
        product_id = int(call.data.split("_")[-1])
        add_product_to_cart(call.message, product_id)
    elif call.data.startswith("remove_one_"):
        product_id = int(call.data.split("_")[-1])
        remove_product_from_cart(call.message, product_id)
    elif call.data == 'goto_cart':
        show_cart(call.message)
    elif call.data.startswith("add_more_cart_"):
        update_cart_items(call, action_type="add_more")
    elif call.data.startswith("remove_one_cart_"):
        update_cart_items(call, action_type="remove_one")
    elif call.data.startswith("remove_all_cart_"):
        update_cart_items(call, action_type="remove_all")
    elif flag == "a":
        # print(data)
        bot.send_message(user_id, "Введите id:")
        bot.register_next_step_handler(call.message, delete, data)

    # При выборе конкретной таблицы из меню админа
    elif flag == "s":
        b = []
        if data == 'users':
            b = ['user_id', 'name', 'phone','address']
        con = sl.connect('delivery_db.db')
        with con:
            data1 = con.execute(f"SELECT * FROM {data}")
            a = data1.fetchall()
        markup_menu = inline_keyboard_admin_bd(data) # изменил название функции создания клавиатуры
        bot.send_message(user_id, f'Таблица {data}')
        bot.send_message(user_id, f'<pre>{tabulate(a, headers=b)}</pre>', parse_mode='HTML', reply_markup=markup_menu)
    # При возврате в "В меню админа" - выпадает список всех доступных таблиц
    elif flag == "b":
        keyboard = send_admin_keyboard()
        bot.send_message(call.message.chat.id, text='Выберите таблицу для редактирования:', reply_markup=keyboard)

    # Нажимаем кнопку "Удалить" после указания id (в любой таблице)
    elif flag == "d":
        keyboard2 = types.InlineKeyboardMarkup()
        keyboard2.add(types.InlineKeyboardButton(data, callback_data=f's{data}'))
        keyboard2.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
        con = sl.connect('delivery_db.db')
        with con:
            # Удаляем запись из выбранной таблицы
            con.execute(f"""DELETE FROM {data} WHERE user_id = ?""", (input_id, ))

        bot.send_message(call.message.chat.id, f'Строка таблицы {data} c id {input_id} удалена!', reply_markup=keyboard2)

    # Нажали кнопку "Внести данные" в любой таблице
    elif flag == "i":
        bot.send_message(call.message.chat.id, f'Внесите данные для заполнения таблицы {data}')
        if data == 'users':
            bot.send_message(user_id, "Введите имя пользователя:")
            bot.register_next_step_handler(call.message, users_name, data)
        if data == 'products':
            bot.send_message(user_id, "Введите название блюда:")
            bot.register_next_step_handler(call.message, products_name, data)

    # Нажали в конкретной таблице кнопку "Изменить данные"
    elif flag == "u":
        bot.send_message(call.message.chat.id, f'Для изменения данных в таблице {data} введите id')
        bot.register_next_step_handler(call.message, update_buttons, data)

    # Нажали кнопку с выбором поля для редактирования
    elif flag == "p":
        buffer_list = data.split('.')
        # print(buffer_list)
        data = buffer_list[0]
        field = buffer_list[1]
        bot.send_message(call.message.chat.id, f'Установите новое значение в таблице {buffer_list[0]} в поле '
                                               f'{buffer_list[1]} c id {update_id}')
        bot.register_next_step_handler(call.message, update_field, data, field)

    # Нажали кнопку "Подтвердить изменения" (при внесении изменений в конкретном поле)
    elif flag == "c":
        con = sl.connect('delivery_db.db')
        buffer_list1 = data.split('.')
        data = buffer_list1[0]
        field = buffer_list1[1]
        with con:
            con.execute(f"""UPDATE {data} SET {field}='{update_value}' WHERE user_id={update_id}""")
        bot.send_message(call.message.chat.id, 'Данные изменены!')
        keyboard7 = types.InlineKeyboardMarkup()
        keyboard7.add(types.InlineKeyboardButton(f'Вернуться в таблицу {data}', callback_data=f's{data}'))
        keyboard7.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='b'))
        bot.send_message(call.message.chat.id, 'Куда идём дальше?', reply_markup=keyboard7)

bot.infinity_polling()
