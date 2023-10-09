from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def send_main_menu_inline():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать', callback_data='begin'))
    keyboard.add(types.InlineKeyboardButton('Отзывы', callback_data='б' + 'reviews'))
    keyboard.add(types.InlineKeyboardButton('О боте', callback_data='about_bot'))
    return keyboard

def send_admin_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Управление данными админов', callback_data='admins_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными блюд', callback_data='й'+'products'))
    keyboard.add(types.InlineKeyboardButton('Управление данными заказов', callback_data='orders_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными пользователей', callback_data='й'+'users'))
    keyboard.add(types.InlineKeyboardButton('Управление данными комментариев', callback_data='comments_data'))
    return keyboard

def send_manager_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Управление данными блюд', callback_data='й'+'products'))
    keyboard.add(types.InlineKeyboardButton('Управление данными заказов', callback_data='orders_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными пользователей', callback_data='й'+'users'))
    keyboard.add(types.InlineKeyboardButton('Управление данными комментариев', callback_data='comments_data'))
    return keyboard

def admin_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('users', callback_data='й' + 'users'))
    keyboard.add(types.InlineKeyboardButton('products', callback_data='й' + 'products'))
    return keyboard

def inline_keyboard_admin_bd(data, button_labels=('Удалить данные', 'Изменить данные', 'Внести данные', 'Вернуться в меню админа')):
    markup_menu = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(button_labels[0], callback_data=f'э{data}')
    btn2 = types.InlineKeyboardButton(button_labels[1], callback_data=f'u{data}')
    btn3 = types.InlineKeyboardButton(button_labels[2], callback_data=f'i{data}')
    btn4 = types.InlineKeyboardButton(button_labels[3], callback_data='b')
    markup_menu.add(btn1, btn2, btn3, btn4)
    return markup_menu

from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатура при нажатии /start
def main_menu_buttons():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать', callback_data='begin'))
    keyboard.add(types.InlineKeyboardButton('Отзывы', callback_data='б' + 'reviews'))
    keyboard.add(types.InlineKeyboardButton('О боте', callback_data='about_bot'))
    return keyboard


# Кнопки меню админа
def admin_menu_buttons():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('users', callback_data='й' + 'users'))
    keyboard.add(types.InlineKeyboardButton('products', callback_data='й' + 'products'))
    keyboard.add(types.InlineKeyboardButton('buffer_reviews', callback_data='n'))
    keyboard.add(types.InlineKeyboardButton('reviews', callback_data='й' + 'reviews'))
    return keyboard

def manager_menu_buttons():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('buffer_reviews', callback_data='n'))
    keyboard.add(types.InlineKeyboardButton('reviews', callback_data='й' + 'reviews'))
    return keyboard

# Клавиатура для принятия решения, публиковать или нет отзыв
def choose_yes_or_no(id_review):
    keyboard_review = types.InlineKeyboardMarkup()
    keyboard_review.add(types.InlineKeyboardButton('Опубликовать', callback_data=f'h{id_review}'))
    keyboard_review.add(types.InlineKeyboardButton('Отклонить комментарий', callback_data=f'y{id_review}'))
    return keyboard_review


# Появляется после нажатия кнопки "Отзывы" в главном меню
def main_menu_reviews():
    keyboard9 = types.InlineKeyboardMarkup()
    keyboard9.add(types.InlineKeyboardButton("Оставить отзыв", callback_data='l'))
    keyboard9.add(types.InlineKeyboardButton("Почитать отзывы", callback_data='j'))
    return keyboard9

def keyboard_cart():
    keyboard_cart = types.InlineKeyboardMarkup()
    keyboard_cart.add(types.InlineKeyboardButton('Перейти в корзину', callback_data='goto_cart'))
    return keyboard_cart
# Появляется после отправки пользователем отзыва
def keyboard_back_review():
    keyboard_back = types.InlineKeyboardMarkup()
    keyboard_back.add(types.InlineKeyboardButton('Вернуться в главное меню', callback_data='z'))
    return keyboard_back


# Появляется для выбора категории блюд для отзыва
def inline_category_keyboard(set_categories):
    category_keyboard = types.InlineKeyboardMarkup()
    for i in set_categories:
        category_keyboard.add(types.InlineKeyboardButton(i[1], callback_data=f'm{i[1]}'))
    return category_keyboard


# Появляется для выбора конкретного блюда для отзыва
def inline_products_keyboard(cat_prod_list):
    products_keyboard = types.InlineKeyboardMarkup()
    for i in cat_prod_list:
        products_keyboard.add(types.InlineKeyboardButton(i[0], callback_data=f'o{i[0]}'))
    return products_keyboard


# Клавиатура для админа, для выбора действий с конкретной таблицей
def inline_admin_menu(data):
    markup_menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('Удалить данные', callback_data=f'э{data}')
    btn2 = InlineKeyboardButton('Изменить данные', callback_data=f'u{data}')
    btn3 = InlineKeyboardButton('Внести данные', callback_data=f'i{data}')
    btn4 = InlineKeyboardButton('Вернуться в меню админа', callback_data='[')
    markup_menu.add(btn1, btn2, btn3, btn4)
    return markup_menu


# Клавиатура для админа, для выбора действий с конкретной таблицей
def inline_keyboard_reviews2():
    keyboard_reviews2 = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('buffer_reviews', callback_data='n')
    btn2 = InlineKeyboardButton('reviews', callback_data='й' + 'reviews')
    keyboard_reviews2.add(btn1, btn2)
    return keyboard_reviews2


# Клавиатура после удаления коментария из buffer_reviews и помещения его в reviews
def inline_keyboard_reviews():
    keyboard_reviews = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton('buffer_reviews', callback_data='n')
    btn2 = InlineKeyboardButton('reviews', callback_data='й' + 'reviews')
    keyboard_reviews.add(btn1, btn2)
    return keyboard_reviews


# Клавиатура для админа, для выбора действий с конкретной таблицей
def inline_products_keyboard2(cat_prod_list):
    products_keyboard2 = types.InlineKeyboardMarkup()
    for i in cat_prod_list:
        products_keyboard2.add(types.InlineKeyboardButton(i[0], callback_data=f't{i[0]}'))
    return products_keyboard2


# Появляется для выбора категории блюд для того, чтобы посмотреть отзывы
def inline_category_keyboard2(set_categories2):
    category_keyboard2 = types.InlineKeyboardMarkup()
    for i in set_categories2:
        category_keyboard2.add(types.InlineKeyboardButton(i[1], callback_data=f'v{i[1]}'))
    return category_keyboard2


# Клавиатура предлагает подтвердить удаление строки после указания id строки
def confirm_delete(data, input_id):
    keyboard1 = types.InlineKeyboardMarkup()
    keyboard1.add(types.InlineKeyboardButton('Удалить', callback_data=f'd{data}.{input_id}'))
    keyboard1.add(types.InlineKeyboardButton(data, callback_data=f'й{data}'))
    keyboard1.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard1


# При неверном указании id строки для удаления
def no_id_delete(data):
    keyboard8 = types.InlineKeyboardMarkup()
    keyboard8.add(types.InlineKeyboardButton(data, callback_data=f'й{data}'))
    keyboard8.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard8


# Действия предлагаются после добавления новой строки в таблицу products
def insert_into_products(data):
    keyboard4 = types.InlineKeyboardMarkup()
    keyboard4.add(types.InlineKeyboardButton(data, callback_data=f'й{data}'))
    keyboard4.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard4


# Клавиатура с полями для изменения (для любой таблицы)
def inline_update_buttons(data, update_id, header_list):
    keyboard5 = types.InlineKeyboardMarkup()
    for i in header_list:
        keyboard5.add(types.InlineKeyboardButton(i, callback_data=f'/{data}.{i}.{update_id}'))
    return keyboard5


# При неверном указании id строки для изменения данных
def no_id_update(data):
    keyboard9 = types.InlineKeyboardMarkup()
    keyboard9.add(types.InlineKeyboardButton(data, callback_data=f'й{data}'))
    keyboard9.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard9


# Для подтверждения изменения значения поля
def inline_update_field(data, field, update_id, update_value):
    keyboard6 = types.InlineKeyboardMarkup()
    keyboard6.add(types.InlineKeyboardButton('Подтвердить изменение',
                                             callback_data=f'ъ{data}.{field}.{update_value}.{update_id}'))
    keyboard6.add(types.InlineKeyboardButton(f'Вернуться в таблицу {data}', callback_data=f'й{data}'))
    keyboard6.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard6


# Клавиатура появляется после подтверждения удаления строки любой таблицы
def after_delete_string(data):
    keyboard2 = types.InlineKeyboardMarkup()
    keyboard2.add(types.InlineKeyboardButton(data, callback_data=f'й{data}'))
    keyboard2.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard2


# Клавиатура появляется после подтверждения внесения изменения в поле таблицы
def after_confirm_update(data):
    keyboard7 = types.InlineKeyboardMarkup()
    keyboard7.add(types.InlineKeyboardButton(f'Вернуться в таблицу {data}', callback_data=f'й{data}'))
    keyboard7.add(types.InlineKeyboardButton('Вернуться в меню админа', callback_data='['))
    return keyboard7


