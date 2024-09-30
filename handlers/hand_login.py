from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from mods import bot_kb
from database import DB
from config import Config
from functools import wraps

r = Router()


def get_user(func):
    @wraps(func)
    async def wrapper(msg: Message, *args, **kwargs):
        user = DB.Users.select({'user_id': msg.chat.id})
        if user == []:
            DB.Users.insert({'user_id': msg.chat.id, 'username': msg.chat.username, 'is_admin': False, 'name': msg.chat.first_name})
            user = DB.Users.select({'user_id': msg.chat.id})
        return await func(msg, user[0], *args, **kwargs)
    return wrapper

@r.message(Command('start'))
@r.message(F.text == "Главное меню")
@get_user
async def command_start(msg: Message, user, state: FSMContext):
    await state.clear()
    await msg.answer(text='Добро пожаловать в меню', reply_markup=bot_kb.menu_kb())

@r.message(Command(Config.Bot.ADMIN_TOKEN))
@get_user
async def command_token(msg: Message, user):
    if not user.is_admin:
        DB.Users.update({'is_admin': True, 'to_notice': True}, {'id': user.id})
        message = 'Вы стали администратором'
    else:
        message = 'Вы уже администратор'
    await msg.answer(text=message, reply_markup=bot_kb.menu_kb())

@r.message(Command(Config.Bot.USER_TOKEN))
@get_user
async def command_token(msg: Message, user):
    if not user.to_notice:
        DB.Users.update({'to_notice': True}, {'id': user.id})
        message = 'Вы подписались на уведомления'
    else:
        message = 'Вы уже подписаны на уведомления'
    await msg.answer(text=message)

