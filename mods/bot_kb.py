from aiogram.types import KeyboardButton as kb_button, ReplyKeyboardMarkup
import consts

def make_kb(els):
    kb = ReplyKeyboardMarkup(keyboard = els, resize_keyboard=True)
    return kb

def back_kb():
    kb = [
            [kb_button(text = 'Главное меню')]
    ]
    return make_kb(kb)

def menu_kb():
    kb = [
            [kb_button(text = 'Добавить игрока')], [kb_button(text = 'Удалить игрока')], [kb_button(text = 'Фильтры')]
    ]
    return make_kb(kb)

def els_kb(els):
    kb = []
    for el in els:
        kb.append([kb_button(text = el)])
    kb.append([kb_button(text = 'Главное меню')])
    return make_kb(kb)

def filter_actions():
    kb = [
            [kb_button(text = 'Страна | добавить'), kb_button(text = 'Страна | удалить')],
            [kb_button(text = 'Спорт | добавить'), kb_button(text = 'Спорт | удалить')],
            [kb_button(text = 'Лига | добавить'), kb_button(text = 'Лига | удалить')],
            [kb_button(text = 'Главное меню')]
    ]
    return make_kb(kb)