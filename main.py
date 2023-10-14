import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3 as sl
import json
import re
from tabulate import tabulate
import keyboardsDelivery
from keyboardsDelivery import send_main_menu_inline, admin_menu_buttons, choose_yes_or_no, main_menu_reviews,\
    keyboard_back_review, inline_category_keyboard, inline_products_keyboard, inline_admin_menu,\
    inline_keyboard_reviews2, inline_keyboard_reviews, inline_products_keyboard2, inline_category_keyboard2,\
    confirm_delete, no_id_delete, inline_update_buttons, no_id_update, inline_update_field,\
    after_delete_string, after_confirm_update,manager_menu_buttons
import sql_queries

con = sl.connect('delivery_db.db', check_same_thread=False)
bot = telebot.TeleBot('6312431700:AAEm_5XrFRy-mzNLSd0uI-lyy1cmWX3aVKA')

bot_description = """
Привет! Я - Ваш помощник-бот. Моя задача - помогать Вам с доставкой еды.
Здесь Вы можете найти следующие возможности:
- "Начать" - Запуск основного функционала;
- "Отзывы" - Узнайте мнение других пользователей о боте;
- "О боте" - Получить информацию обо мне.
"""
header_users = ['name', 'phone', 'address', 'telegram_id']
header_products = ['name', 'description', 'price', 'amount', 'category','photo']
header_reviews = ['user_id', 'product_id', 'comment', 'user_rating']
header_categories = ['category_name']
header_admins = ['login', 'password']
header_orders = ['user_id', 'cart_id', 'address', 'delivery_time', 'payment']
header_cart_items = ['cart_id', 'product_id', 'amount']
header_cart = ['user_id']
header_list = []

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, text='Выберите действие:', reply_markup=send_main_menu_inline())

########################Добавление нового пользователя#################
question_dict = {
    "name": "Введите имя:",
    "phone": "Введите номер телефона:",
    "address": "Введите ваш адрес",
}
PHONE_RE = re.compile(r"^(\+375|80)(29|25|44|33)(\d{3})(\d{2})(\d{2})$")
new_user = {}
def start_new_user(message):
    username = message.chat.username
    telegram_id = message.chat.id
    if not user_exists(telegram_id):
        new_user[telegram_id] = {'telegram_id': telegram_id, 'questions': iter(question_dict.items())}
        ask_next_question(telegram_id)
    else:
        bot.send_message(chat_id=telegram_id, text=f"Добро пожаловать, {username}!")


def ask_next_question(telegram_id):
    try:
        question, prompt = next(new_user[telegram_id]['questions'])
        new_user[telegram_id]['next_question'] = question
        bot.send_message(chat_id=telegram_id, text=prompt)
    except StopIteration:
        bot.send_message(chat_id=telegram_id, text='Вы успешно прошли регистрацию.', reply_markup=send_main_menu_inline())
        add_user_in_db(new_user.pop(telegram_id))


def add_user_in_db(user_data):
    username = user_data.get('name')
    phone = user_data.get('phone')
    address = user_data.get('address')
    telegram_id = user_data['telegram_id']
    add_user(username, phone, address, telegram_id)


# save_answer cохраняет ответ пользователя на вопрос и вызывает следующий вопрос.
@bot.message_handler(func=lambda message: message.chat.id in new_user)
def save_answer(message):
    answer = message.text
    telegram_id = message.chat.id
    question = new_user[telegram_id]['next_question']
    if question == "phone" and not PHONE_RE.match(answer):
        bot.send_message(chat_id=telegram_id, text="Введите номер телефона в правильном формате.")
    else:
        new_user[telegram_id][question] = answer
        ask_next_question(telegram_id)


def user_exists(telegram_id):  # Проверяет если пользователь в БД
    with con:
        result = con.execute(sql_queries.SELECT_USER_QUERY, (telegram_id,)).fetchone()
    return result


def add_user(username, phone=None, address=None, telegram_id=None):  # Записывает пользвателя в ДБ
    with con:
        con.execute(sql_queries.INSERT_USER_QUERY,
                    (username, phone, address, telegram_id))
        con.commit()
##################Конец добавления нового пользователя######################


##################Вход в Админ панель#######################################
def request_admin_credentials(message):
    msg = bot.send_message(message.chat.id, "Введите ваш логин:")
    bot.register_next_step_handler(msg, process_admin_login)
def process_admin_login(message):
    login = message.text
    msg = bot.send_message(message.chat.id, "Введите ваш пароль:")
    bot.register_next_step_handler(msg, lambda message: process_admin_password(message, login))
def process_admin_password(message, login):
    password = message.text
    user_id = message.chat.id
    user = check_admin_credentials(login, password)
    if user:
        if user[2] == 'admin':
            bot.send_message(user_id, text='Выберите таблицу для редактирования:',
                             reply_markup=admin_menu_buttons())
        elif user[2] == 'manager':
            bot.send_message(user_id, text='Выберите таблицу для редактирования:',
                             reply_markup=manager_menu_buttons())
    else:
        bot.send_message(message.chat.id, "Неверные учетные данные. Пожалуйста, попробуйте еще раз.")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    request_admin_credentials(message)

def check_admin_credentials(login, password):
    with con:
        result_admin = con.execute(sql_queries.SELECT_ADMINS_QUERY, (login, password)).fetchone()
        result_manager = con.execute(sql_queries.SELECT_MANAGERS_QUERY, (login, password)).fetchone()
    if result_admin:
        return result_admin[0], result_admin[1], 'admin'
    elif result_manager:
        return result_manager[0], result_manager[1], 'manager'

    return None
###########################Конец Панель входа Админ################################


######################################################################################
# БЛОК: АДМИНА
######################################################################################

######################################################################################
# УДАЛЕНИЕ СТРОКИ ИЗ ЛЮБОЙ ВЫБРАННОЙ ТАБЛИЦЫ
######################################################################################


# Функция принимает id строки, которую нужно удалить из таблицы
def delete(message, data):
    id_list = []
    input_id = message.text
    try:
        input_id = int(input_id)
    except ValueError:
        pass
    with con:
        id_exist = con.execute(f"""SELECT id FROM {data} """)
        id_exist = (id_exist.fetchall())
        for i in id_exist:
            id_list.append(i[0])
    if input_id in id_list:
        bot.send_message(message.chat.id, text='Что делаем дальше c данными?',
                         reply_markup=confirm_delete(data, input_id))
    else:
        bot.send_message(message.chat.id, text='Нет такого id')
        bot.send_message(message.chat.id, text='Что делаем дальше?', reply_markup=no_id_delete(data))

################################################################################################
# ДОБАВЛЕНИЕ СТРОКИ В ЛЮБУЮ ТАБЛИЦУ - НАЧАЛО
################################################################################################
# Запросы к пользователю для каждого поля каждой таблицы
questions_dict = {
    "admins": {
        "login": "Введите логин:",
        "password": "Введите пароль:",
    },
    "managers": {
        "login": "Введите логин:",
        "password": "Введите пароль:",
    },
    "products": {
        "product_name": "Введите название продукта:", # Было product_name
        "description": "Введите описание продукта:",
        "price": "Введите цену продукта:",
        "amount": "Введите количество продукта:",
        "category": "Введите категорию продукта:",
    },
    "categories": {
        "category_name": "Введите название категории:",
    },
    "users": {
        "name": "Введите ваше имя:",
        "phone": "Введите номер вашего телефона:",
        "address": "Введите ваш адрес:",
        "telegram_id": "Введите telegram_id:",
    },
    "reviews": {
        "user_id": "Введите user_id:",
        "product_id": "Введите product_id:",
        "comment": "Введите отзыв:",
        "user_rating": "Введите рейтинг:",
    },
    "orders": {
        "user_id": "Введите user_id:",
        "cart_id": "Введите cart_id:",
        "address": "Введите адрес:",
        "delivery_time": "Введите время доставки:",
        "payment": "Введите способ оплаты:",
    },
    "cart_items": {
        "cart_id": "Введите cart_id:",
        "product_id": "Введите product_id:",
        "amount": "Введите amount",
    },
    "cart": {
        "user_id": "Введите user_id:",
    },
}


# Задаем вопросы для заполнения полей
def ask_for_field(message, data, fields_iterator, answers=None):
    try:
        field, question = next(fields_iterator) # Получаем следующее поле и вопрос
    except StopIteration:  # Если поля закончились, совершаем вставку в базу данных
        insert_into_table(message, data, answers)
        return
    if answers is None:
        answers = {}  # Инициализируем словарь ответов, если он еще не создан
    bot.send_message(message.chat.id, question)
    bot.register_next_step_handler(message, get_answer, data, field, fields_iterator, answers)  # Регистрируем обработчик следующего шага


# Получаем ответ пользователя на вопрос
def get_answer(message, data, field, fields_iterator, answers):
    answers[field] = message.text  # Сохраняем ответ
    ask_for_field(message, data, fields_iterator, answers)  # Задаем следующий вопрос или вставляем в базу д


# Функция для добавления записи в таблицу
def insert_into_table(message, data, answers):
    # Строка запроса
    query = f"""INSERT INTO {data}({', '.join(answers.keys())}) VALUES ({', '.join(['?'] * len(answers))})"""
    # Выполнение запроса
    with con:
        con.execute(query, list(answers.values()))
    bot.send_message(message.chat.id, f"Данные добавлены в таблицу {data}.", reply_markup=admin_menu_buttons())

################################################################################################
# ДОБАВЛЕНИЕ СТРОКИ В ЛЮБУЮ ТАБЛИЦУ - КОНЕЦ
################################################################################################

################################################################################################
# ИЗМЕНЕНИЕ ДАННЫХ В ПОЛЕ ЛЮБОЙ ТАБЛИЦЫ - НАЧАЛО
################################################################################################


# Функция предлагает набор кнопок, полей таблицы, после указания строки для редактирования
def update_buttons(message, data):
    global header_list
    update_id = message.text
    update_id_list = []
    if data == 'cart':
        header_list = header_cart
    if data == 'cart_items':
        header_list = header_cart_items
    if data == 'orders':
        header_list = header_orders
    if data == 'categories':
        header_list = header_categories
    if data == 'admins' or data == 'managers':
        header_list = header_admins
    if data == 'users':
        header_list = header_users
    if data == 'products':
        header_list = header_products
    if data == 'reviews':
        header_list = header_reviews
    if data == 'categories':
        header_list = header_categories
    try:
        update_id = int(update_id)
    except ValueError:
        pass
    with con:
        update_id_exist = con.execute(f"""SELECT id FROM {data} """)
        update_id_exist = (update_id_exist.fetchall())
        for i in update_id_exist:
            update_id_list.append(i[0])
    if update_id in update_id_list:
        bot.send_message(message.chat.id, f"Выберите поле таблицы {data} и редактируйте его",
                         reply_markup=inline_update_buttons(data, update_id, header_list))
    else:
        bot.send_message(message.chat.id, text='Нет такого id')
        bot.send_message(message.chat.id, text='Что делаем дальше?',
                         reply_markup=no_id_update(data))


# Функция принимает изменённое значение поля
def update_field(message, data, field, update_id):
    update_value = message.text
    bot.send_message(message.chat.id, f"Изменить значение поля {field} в таблице {data} с "
                                      f"id {update_id} на {update_value}?",
                     reply_markup=inline_update_field(data, field, update_id, update_value))


################################################################################################
# ИЗМЕНЕНИЕ ДАННЫХ В ПОЛЕ ЛЮБОЙ ТАБЛИЦЫ - КОНЕЦ
################################################################################################
######################################################################################
# ОТЗЫВЫ
######################################################################################

# Функция принимает отзыв и просит ввести рейтинг
def input_rating(message, data):
    buffer_review = message.text
    bot.send_message(message.chat.id, "Поставьте, пожалуйста, оценку от 1 до 5")
    bot.register_next_step_handler(message, input_review, data, buffer_review)


# Функция отправляет отзыв в буферную таблицу
def input_review(message, data, buffer_review):
    id_user = message.from_user.id
    buffer_rating = message.text
    try:
        buffer_rating = int(buffer_rating)
    except ValueError:
        pass
    if type(buffer_rating) == int and 1 <= buffer_rating <= 5:
        with con:
            data_product_id = con.execute(f"""SELECT id FROM products
                                WHERE product_name = '{data}'""")
            product_id_set = data_product_id.fetchall()
        product_id = product_id_set[0][0]
        insert_buffer_review = "INSERT INTO buffer_reviews (user_id, product_id, comment, rating) values (?, ?, ?, ?)"
        buffer_review_list = (id_user, product_id, buffer_review, buffer_rating)
        with con:
            con.execute(insert_buffer_review, buffer_review_list)
        bot.send_message(message.chat.id, "Спасибо! Ваш отзыв будет опубликован после одобрения администратором",
                         reply_markup=keyboard_back_review())
    elif type(buffer_rating) == str or 5 <= buffer_rating or buffer_rating <= 1:
        buffer_rating = 4
        bot.send_message(message.chat.id, "Оценка указана неверно, оценка по умолчанию <b>4</b>",
                         parse_mode='HTML')
        with con:
            data_product_id = con.execute(f"""SELECT id FROM products
                                WHERE product_name = '{data}'""")
            product_id_set = data_product_id.fetchall()
        product_id = product_id_set[0][0]
        insert_buffer_review = "INSERT INTO buffer_reviews (user_id, product_id, comment, rating) values (?, ?, ?, ?)"
        buffer_review_list = (id_user, product_id, buffer_review, buffer_rating)
        with con:
            con.execute(insert_buffer_review, buffer_review_list)
        bot.send_message(message.chat.id, "Спасибо! Ваш отзыв будет опубликован после одобрения администратором",
                         reply_markup=keyboard_back_review())


# Функция принимает id комментария и предлагает публиковать/не публиковать отзывы - для админа
def yes_or_no(message):
    id_review = message.text
    try:
        id_review = int(id_review)
        id_list = []
        with con:
            existing_id = con.execute("""SELECT id FROM buffer_reviews""")
            existing_id = existing_id.fetchall()
            print(existing_id)
        for i in existing_id:
            id_list.append(i[0])
        if id_review in id_list:
            bot.send_message(message.chat.id, f"Опубликовать комментарий c id {id_review}?", reply_markup=choose_yes_or_no(id_review))
        else:
            bot.send_message(message.chat.id, "id указан неверно, выберите id из таблицы")
            bot.register_next_step_handler(message, yes_or_no)
    except:
        bot.send_message(message.chat.id, "id указан неверно, выберите id из таблицы")
        bot.register_next_step_handler(message, yes_or_no)


###########################Кактегории блюд#########################################
def send_categories_keyboard(message):
    keyboard = types.InlineKeyboardMarkup()
    with con:
        categories = con.execute("SELECT * FROM categories").fetchall()

    for category in categories:
        keyboard.add(types.InlineKeyboardButton(category[1], callback_data=f"category_{category[0]}"))

    bot.send_message(message.chat.id, text='Выберите категорию:', reply_markup=keyboard)


user_messages = {}  # Для сохранения списка сообщений с блюдами для каждого пользователя


def send_dishes_by_category(message, category_id):
    telegram_id = message.chat.id
    with con:
        dishes = con.execute("SELECT * FROM products WHERE category = ?", (category_id,)).fetchall()

    messages_to_delete = []  # Сохраняет весь список message_id с блюдами
    for dish in dishes:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton('Добавить в корзину', callback_data=f"add_to_cart_{dish[0]}"),

        )

        dish_text = f"Название: {dish[1]}\nОписание: {dish[2]}\nЦена: {dish[3]} руб\n"
        image_path = dish[6]

        photo_message = bot.send_photo(chat_id=message.chat.id, photo=open(image_path, 'rb'))
        messages_to_delete.append(photo_message.message_id)

        sent_message = bot.send_message(chat_id=message.chat.id, text=dish_text, reply_markup=keyboard)
        messages_to_delete.append(sent_message.message_id)

    user_messages[telegram_id] = messages_to_delete  # Сохраняет список message_id для каждого пользователя
    keyboard_back = types.InlineKeyboardMarkup()
    keyboard_back.add(types.InlineKeyboardButton("Перейти в корзину", callback_data="goto_cart"))
    keyboard_back.add(types.InlineKeyboardButton("Назад", callback_data="back_to_categories"))
    back_message = bot.send_message(chat_id=message.chat.id, text=f"Нажмите 'Перейти в корзину' для дальнейшего оформления заказа.\nНажмите 'Назад', чтобы вернуться к категориям",
                                    reply_markup=keyboard_back)
    user_messages[telegram_id].append(back_message.message_id)  # Сохраняет message_id сообщения с кнопкой "Назад"



#################################Конец########################################

############################Корзина###########################################
def show_cart(message, edit=False):
    user_id = message.chat.id
    with con:
        cart_items = con.execute("""
                SELECT p.id, p.product_name, p.price, ci.amount
                FROM cart_items ci
                INNER JOIN products p ON p.id = ci.product_id
                INNER JOIN cart c ON c.id = ci.cart_id
                WHERE c.user_id = ?""", (user_id,)).fetchall()

    if len(cart_items) == 0:
        bot.send_message(chat_id=user_id, text="Ваша корзина пуста!")
        return

    total_cost = 0
    bot.send_message(message.chat.id, text="Корзина:")
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
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=dish_text, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, text=dish_text, reply_markup=keyboard)

    bot.send_message(message.chat.id, text=f"Итого: {total_cost} руб")
    send_delivery_options(message)


def update_cart_items(call, action_type):
    user_id = call.message.chat.id
    product_id = int(call.data.split("_")[-1])

    with con:
        product_name = con.execute("SELECT product_name FROM products WHERE id = ?", (product_id,)).fetchone()[0]
        cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()
        cart_id = cart_id[0] if cart_id else None
        if cart_id is None:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Вашей корзины не существует!")
            return

        item_in_cart = con.execute("SELECT amount FROM cart_items WHERE cart_id = ? AND product_id = ?",
                                   (cart_id, product_id)).fetchone()
        if item_in_cart:
            if action_type == "add_more":
                con.execute("UPDATE cart_items SET amount = amount + 1 WHERE  cart_id = ? AND product_id = ?",
                            (cart_id, product_id))
                bot.send_message(user_id, f"Вы добавили ещё один {product_name} в корзину.")
            elif action_type == "remove_one" and item_in_cart[0] > 1:
                con.execute("UPDATE cart_items SET amount = amount - 1 WHERE cart_id = ? AND product_id = ?",
                            (cart_id, product_id))
                bot.send_message(user_id, f"Вы убрали один {product_name} из корзины.")
            elif action_type == "remove_one" and item_in_cart[0] == 1:
                con.execute("DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, product_id))
            elif action_type == "remove_all":
                con.execute("DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, product_id))
                bot.send_message(user_id, f"Вы убрали все {product_name} из корзины.")
            con.commit()

            show_cart(call.message, edit=True)
        else:
            bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
                                      text="Этот товар отсутствует в корзине!")


user_last_add_message = {}  # Для сохранения последнего сообщения с добавлением товара в корзину для каждого пользователя


def add_product_to_cart(message, product):
    user_id = message.chat.id
    with con:
        product_name = con.execute("SELECT product_name FROM products WHERE id = ?", (product,)).fetchone()[0]
        cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()
        cart_id = cart_id[0] if cart_id else None

        if cart_id is None:
            con.execute("INSERT INTO cart(user_id) VALUES (?);", (user_id,));
            cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()[0]

        existing_product = con.execute("SELECT amount FROM cart_items WHERE cart_id = ? AND product_id = ?",
                                       (cart_id, product)).fetchone()

        if existing_product:
            con.execute("UPDATE cart_items SET amount = amount + 1 WHERE cart_id = ? AND product_id = ?",
                        (cart_id, product))
            bot.send_message(user_id, f"Вы добавили ещё один {product_name} в корзину.", reply_markup= keyboardsDelivery.keyboard_cart())

        else:
            con.execute("INSERT INTO cart_items(cart_id, product_id, amount) VALUES (?, ?, 1)", (cart_id, product))
            bot.send_message(user_id, f"Вы добавили {product_name} в корзину.",)

        con.commit()


def remove_product_from_cart(message, product_id):
    user_id = message.chat.id
    with con:
        product_name = con.execute("SELECT product_name FROM products WHERE id = ?", (product_id,)).fetchone()[0]
        cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()
        cart_id = cart_id[0] if cart_id else None

        if cart_id is None:
            bot.send_message(chat_id=message.chat.id, text="Вашей корзины не существует!")
            return

        existing_product = con.execute("SELECT amount FROM cart_items WHERE cart_id = ? AND product_id = ?",
                                       (cart_id, product_id)).fetchone()

        if existing_product and existing_product[0] > 1:
            con.execute("UPDATE cart_items SET amount = amount - 1 WHERE cart_id = ? AND product_id = ?",
                        (cart_id, product_id))
            bot.send_message(user_id, f"Вы убрали один {product_name} из корзины.",reply_markup= keyboardsDelivery.keyboard_cart())
        elif existing_product and existing_product[0] == 1:
            con.execute("DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?", (cart_id, product_id))
            bot.send_message(user_id, f"Вы удалили все {product_name} из корзины.")
        else:
            bot.send_message(chat_id=message.chat.id, text="Товар отсутствует в корзине!")

        con.commit()


#############################Конец#####################################

#############################Оформление доставки#######################
def send_delivery_options(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Самовывоз', callback_data='self_pickup'),
        types.InlineKeyboardButton('Доставка курьером', callback_data='courier')
    )
    bot.send_message(message.chat.id, "Выберите способ доставки", reply_markup=keyboard)


#############################Конец#####################################


def category_id_exists(category_id):
    with con:
        existed_category_ids = con.execute("SELECT category_id FROM categories")
        existed_category_ids = [item[0] for item in existed_category_ids.fetchall()]
    return category_id in existed_category_ids


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    bot.answer_callback_query(callback_query_id=call.id)
    user_id = call.message.chat.id
    data = call.data[1:]
    flag = call.data[0]
    if call.data == "begin":
        telegram_id = call.message.chat.id
        username = call.message.chat.first_name
        if not user_exists(telegram_id):
            start_new_user(call.message)
        else:
            with con:
                con.execute("DELETE FROM cart_items WHERE cart_id = ?", (telegram_id,))  # очистка корзины через cart_id
                con.commit()

            menu_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Главное меню")
            menu_button.add(btn1)
            bot.send_message(chat_id=telegram_id, text=f"Добро пожаловать, {username}!",reply_markup=menu_button)
            send_categories_keyboard(call.message)

    elif call.data == 'about_bot':
        bot.send_message(call.message.chat.id, text=bot_description)
    elif call.data.startswith("category_"):
        category_id = int(call.data.split("_")[-1])
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)  # Удаление сообщения с категориями
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
    elif call.data == 'self_pickup':
        handle_self_pickup(call)
    elif call.data == 'courier':
        handle_courier(call)##########
    elif call.data.startswith('pay_'):
        handle_payment_method(call)
    elif call.data == 'delivery_options':
        send_delivery_options(call)
        # Нажали кнопку "Отзывы" в главном меню
    if flag == "б":
        bot.send_message(user_id, "Выберите действие:", reply_markup=main_menu_reviews())
        # Нажали кнопку "Оставить отзыв" - выпадает список с категориями продуктов
    if flag == "l":
        select_categories = con.execute("SELECT * FROM categories")
        set_categories = select_categories.fetchall()
        bot.send_message(user_id, "Выберите категорию:", reply_markup=inline_category_keyboard(set_categories))

        # Нажали кнопку с категорией, чтобы оставить отзыв - выпадает список блюд данной категории
    if flag == "m":
        with con:
            cat_prod_table = con.execute("""SELECT product_name FROM products
                                   INNER JOIN categories
                                   ON products.category = categories.id
                                   WHERE category_name = ?
                                   """, (data,))
            cat_prod_list = cat_prod_table.fetchall()
        bot.send_message(user_id, f'Выберите продукт категории "{data}": ',
                         reply_markup=inline_products_keyboard(cat_prod_list))

        # Выбрали конкретный продукт, чтобы оставить отзыв
    if flag == "o":
        bot.send_message(user_id, 'Напишите Ваш отзыв одним сообщением:')
        bot.register_next_step_handler(call.message, input_rating, data)

        # Нажали кнопку "Вернуться в главное меню" после того, как оставили отзыв о блюде
    if flag == "z":
        bot.send_message(call.message.chat.id, text='Выберите действие:', reply_markup=send_main_menu_inline())

        # При выборе конкретной таблицы из меню админа
    if flag == "й":
        b = []
        if data == 'cart':
            b = ['id', 'user_id']
        if data == 'cart_items':
            b = ['cart_id', 'product_id', 'amount']
        if data == 'orders':
            b = ['id', 'user_id', 'cart_id', 'address', 'delivery_time', 'payment']
        if data == 'admins' or data == 'managers':
            b = ['id', 'login', 'password']
        if data == 'users':
            b = ['id', 'name', 'phone', 'address', 'telegram_id']
        if data == 'products':
            b = ['id', 'product_name', 'description', 'price', 'amount', 'category','photo']
        if data == 'reviews':
            b = ['id', 'user_id', 'product_id', 'comment', 'user_rating']
        if data == 'categories':
            b = ['id', 'category_name']
        with con:
            data1 = con.execute(f"SELECT * FROM {data}")
            a = data1.fetchall()
        bot.send_message(user_id, f'Таблица <b>{data}</b>', parse_mode='HTML')
        bot.send_message(user_id, f'<pre>{tabulate(a, headers=b)}</pre>', parse_mode='HTML',
                         reply_markup=inline_admin_menu(data))

        # При выборе таблицы buffer_reviews из меню админа
    if flag == "n":# прописать условие что если нет такого id
        b = ['id', 'user_id', 'product_id', 'comment', 'rating']
        with con:
            data1 = con.execute(f"SELECT * FROM buffer_reviews")
            a = data1.fetchall()
            if len(a) != 0:
                bot.send_message(user_id, f'Таблица <b>buffer_reviews</b>', parse_mode='HTML')
                bot.send_message(user_id, f'<pre>{tabulate(a, headers=b)}</pre>', parse_mode='HTML')
                bot.send_message(user_id, 'Введите id комментария для дальнейшей работы с ним')
                bot.register_next_step_handler(call.message, yes_or_no)
            else:
                bot.send_message(user_id, 'В буферной таблице пока нет комментариев')
                bot.send_message(call.message.chat.id, text='Выберите таблицу для редактирования:',
                                 reply_markup=admin_menu_buttons())

        # Появляется после нажатия кнопки "Удалить комментарий" из buffer_reviews
    if flag == "y":
        data = int(data)
        with con:
            cat_prod_table = con.execute(f"""DELETE FROM buffer_reviews WHERE id = {data}""")
        bot.send_message(user_id, 'Комментарий удалён!', reply_markup=inline_keyboard_reviews2())

        # После нажатия на кнопку "Опубликовать комментарий"
    if flag == "h":
        with con:
            current_info = con.execute(f"""SELECT * FROM buffer_reviews
                                   WHERE id = {int(data)}
                                   """)
            current_info_set = current_info.fetchall()

        with con:
            con.execute("""INSERT INTO reviews (user_id, product_id, comment, user_rating) 
               values (?, ?, ?, ?)""", (current_info_set[0][1],
                                        current_info_set[0][2],
                                        current_info_set[0][3],
                                        current_info_set[0][4]))

        with con:
            cat_prod_table = con.execute(f"""DELETE FROM buffer_reviews WHERE id = {int(data)}""")
        bot.send_message(user_id, 'Комментарий удалён из таблицы <b>buffer_reviews</b>', parse_mode='HTML')
        bot.send_message(user_id, 'Комментарий добавлен в таблицу <b>reviews</b>', parse_mode='HTML',
                         reply_markup=inline_keyboard_reviews())

        # Список категорий для пользователя, который хочет посмотреть отзывы
    if flag == "j":
        select_categories = con.execute("SELECT * FROM categories")
        set_categories2 = select_categories.fetchall()
        bot.send_message(user_id, "Выберите категорию:",
                         reply_markup=inline_category_keyboard2(set_categories2))

        # Список продуктов, появляется после выбора категории (когда пользователь хочет просмотреть озывы)
    if flag == "v":
        with con:
            cat_prod_table = con.execute("""SELECT product_name FROM products
                                           INNER JOIN categories
                                           ON products.category = categories.id
                                           WHERE category_name = ?
                                           """, (data,))
            cat_prod_list = cat_prod_table.fetchall()
        bot.send_message(user_id, f'Выберите продукт категории "{data}": ',
                         reply_markup=inline_products_keyboard2(cat_prod_list))

        # После нажатия на кнопку с конкретным продуктом для просмотра отзыва
    if flag == "t":
        c = ['Отзыв', 'Рейтинг']
        try:
            with con:
                comment_list = con.execute("""SELECT comment, user_rating FROM reviews
                                               INNER JOIN products
                                               ON products.id = reviews.product_id
                                               WHERE product_name = ?
                                               """, (data,))
                comment_list = comment_list.fetchall()
                reviews_number = len(comment_list)
                sum = 0
                for i in comment_list:
                    sum += i[1]
                average_rating = round(sum / reviews_number, 1)
            bot.send_message(user_id, f'Отзывы о <b>{data}</b>', parse_mode='HTML')
            bot.send_message(user_id, f'<pre>{tabulate(comment_list, headers=c)}</pre>', parse_mode='HTML')
            bot.send_message(user_id, f'Средний рейтинг <b>{data}</b> равен <b>{average_rating}</b>',
                             parse_mode='HTML', reply_markup=send_main_menu_inline())
        except:
            bot.send_message(user_id, text="К данному блюду отсутствуют отзывы.", reply_markup=send_main_menu_inline())

    # Нажали кнопку "Удалить данные" в любой таблице
    if flag == "э":
        bot.send_message(user_id, "Введите id:")
        bot.register_next_step_handler(call.message, delete, data)

        # При возврате в "В меню админа" - выпадает список всех доступных таблиц
    if flag == "[":
        bot.send_message(call.message.chat.id, text='Выберите таблицу для редактирования:',
                         reply_markup=admin_menu_buttons())

        # Нажали кнопку "Удалить" после указания id (в любой таблице)
    if flag == "d":
        buffer_list = data.split('.')
        data = buffer_list[0]
        input_id = buffer_list[1]
        with con:
            con.execute(f"""DELETE FROM {data} WHERE id = ?""", (input_id,))
        bot.send_message(call.message.chat.id, f'Строка таблицы {data} c id {input_id} удалена!',
                         reply_markup=after_delete_string(data))

        # Нажали кнопку "Внести данные" в любой таблице
    if flag == "i":
        bot.send_message(call.message.chat.id, f'Внесите данные для заполнения таблицы {data}')
        ask_for_field(call.message, data, iter(questions_dict[data].items()))

        # Нажали в любой таблице кнопку "Изменить данные"
    if flag == "u":
        bot.send_message(call.message.chat.id, f'Для изменения данных в таблице {data} введите id')
        bot.register_next_step_handler(call.message, update_buttons, data)

        # Нажали кнопку с выбором поля для редактирования
    if flag == "/":
        buffer_list = data.split('.')
        data = buffer_list[0]
        print(data)
        field = buffer_list[1]
        print(field)
        update_id = buffer_list[2]
        bot.send_message(call.message.chat.id, f'Установите новое значение в таблице {data} в поле '
                                               f'{field} c id {update_id}')
        bot.register_next_step_handler(call.message, update_field, data, field, update_id)

        # Нажали кнопку "Подтвердить изменения" (при внесении изменений в конкретном поле)
    if flag == "ъ":
        buffer_list1 = data.split('.')
        data = buffer_list1[0]
        field = buffer_list1[1]
        update_value = buffer_list1[2]
        update_id = buffer_list1[3]
        with con:
            con.execute(f"""UPDATE {data} SET {field}='{update_value}' WHERE id={update_id}""")
        bot.send_message(call.message.chat.id, 'Данные изменены!')
        bot.send_message(call.message.chat.id, 'Куда идём дальше?', reply_markup=after_confirm_update(data))


@bot.message_handler(func=lambda message: True)  # обработчик всех текстовых сообщений
def handle_text(message):
    if message.text == 'Главное меню':
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=send_main_menu_inline())


def handle_self_pickup(call):
    user_id = call.message.chat.id
    cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()[0]
    bot.send_message(call.message.chat.id,
                     "Вы выбрали самовывоз. Наш адрес: Независимости 76. Заказ будет готов через 45 минут.")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Оплата картой', callback_data=f'pay_card_{cart_id}'),
        types.InlineKeyboardButton('Оплата наличными', callback_data=f'pay_cash_{cart_id}'),
        types.InlineKeyboardButton('Оплата онлайн', callback_data=f'pay_online_{cart_id}')
    )
    bot.send_message(call.message.chat.id, "Пожалуйста, выберите способ оплаты.",
                     reply_markup=keyboard)
    add_order_to_db(user_id, cart_id, None)


def add_order_to_db(user_id, cart_id, payment, address=None, delivery_time=None):
    with con:
        con.execute("""
        INSERT INTO orders(user_id, cart_id, payment, address, delivery_time)
        VALUES (?, ?, ?, ?, ?)
        """, (user_id, cart_id, payment, address, delivery_time))
        con.commit()


def handle_courier(call):
    user_id = call.message.chat.id
    with con:
        address_row = con.execute("SELECT address FROM users WHERE telegram_id = ?", (user_id,)).fetchone()
        if address_row is None:
            bot.send_message(call.message.chat.id,
                             "Ваш адрес не найден в базе данных. Пожалуйста, добавьте его.")
            return
        address = address_row[0]
        cart_id = con.execute("SELECT id FROM cart WHERE user_id = ?", (user_id,)).fetchone()[0]

    bot.send_message(call.message.chat.id,
                     f"Вы выбрали доставку курьером. Ваш адрес доставки: {address}. Заказ будет доставлен в течении 60 минут.")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton('Оплата картой', callback_data=f'pay_card_{cart_id}'),
        types.InlineKeyboardButton('Оплата наличными', callback_data=f'pay_cash_{cart_id}'),
        types.InlineKeyboardButton('Оплата онлайн', callback_data=f'pay_online_{cart_id}')
    )
    bot.send_message(call.message.chat.id, "Пожалуйста, выберите способ оплаты.",
                     reply_markup=keyboard)
    add_order_to_db(user_id, cart_id, None, address, "60 минут")


@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_'))
def handle_payment_method(call):
    payment_method = call.data.split('_')[1]
    cart_id = int(call.data.split('_')[2])
    with con:
        con.execute("UPDATE orders SET payment = ? WHERE cart_id = ?", (payment_method, cart_id))
        con.execute("DELETE FROM cart_items WHERE cart_id = ?", (cart_id,))  # удаление записей корзины
        con.commit()
    bot.send_message(call.message.chat.id, f"Вы оплатили {payment_method}. Ваш заказ подтверждён!")
    bot.send_message(call.message.chat.id, "Главное меню:", reply_markup=send_main_menu_inline())


print('Ready')
bot.infinity_polling(skip_pending=True)
