from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
def send_main_menu_inline():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать', callback_data='begin'))
    keyboard.add(types.InlineKeyboardButton('Отзывы', callback_data='reviews'))
    keyboard.add(types.InlineKeyboardButton('О боте', callback_data='about_bot'))
    return keyboard


def send_admin_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Управление данными админов', callback_data='admins_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными блюд', callback_data='s'+'products'))
    keyboard.add(types.InlineKeyboardButton('Управление данными заказов', callback_data='orders_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными пользователей', callback_data='s'+'users'))
    keyboard.add(types.InlineKeyboardButton('Управление данными комментариев', callback_data='comments_data'))
    return keyboard

def send_manager_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Управление данными блюд', callback_data='s'+'products'))
    keyboard.add(types.InlineKeyboardButton('Управление данными заказов', callback_data='orders_data'))
    keyboard.add(types.InlineKeyboardButton('Управление данными пользователей', callback_data='s'+'users'))
    keyboard.add(types.InlineKeyboardButton('Управление данными комментариев', callback_data='comments_data'))
    return keyboard

def admin_menu_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('users', callback_data='s' + 'users'))
    keyboard.add(types.InlineKeyboardButton('products', callback_data='s' + 'products'))
    return keyboard


def inline_keyboard_admin_bd(data, button_labels=('Удалить данные', 'Изменить данные', 'Внести данные', 'Вернуться в меню админа')):
    markup_menu = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(button_labels[0], callback_data=f'a{data}')
    btn2 = types.InlineKeyboardButton(button_labels[1], callback_data=f'u{data}')
    btn3 = types.InlineKeyboardButton(button_labels[2], callback_data=f'i{data}')
    btn4 = types.InlineKeyboardButton(button_labels[3], callback_data='b')
    markup_menu.add(btn1, btn2, btn3, btn4)
    return markup_menu

