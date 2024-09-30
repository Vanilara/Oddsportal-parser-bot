from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Filter
from aiogram.types import message
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from database import DB
from mods import bot_kb, bot_states

r = Router()


class FilterAdmin(Filter):
    def __init__(self, is_admin):
        self.is_admin = is_admin

    async def __call__(self, msg: Message):
        user_id = msg.chat.id
        cur_user = DB.Users.select({'user_id': user_id})[0]
        return cur_user.is_admin

@r.message(FilterAdmin(Message), F.text == "Фильтры")
async def players(msg: Message, state: FSMContext):
    await state.set_state(bot_states.filter_setts.player)
    message = 'Текущие игроки:\n'
    players = []
    kounter = 0
    for player in DB.Players.select():
        kounter += 1
        message += f'{kounter}. {player.name}\n'
        players.append(player.name)
    message += '\nВыберите игрока на клавиатуре для добавления слов фильтрации'
    await msg.answer(text = message, reply_markup=bot_kb.els_kb(players))

@r.message(FilterAdmin(Message), F.text == "Добавить игрока")
async def add_player_start(msg: Message, state: FSMContext):
    await state.set_state(bot_states.add_user.take)
    await msg.answer(text = 'Отправьте имя игрока', reply_markup=bot_kb.back_kb())

@r.message(bot_states.add_user.take)
async def add_player_finish(msg: Message, state: FSMContext):
    DB.Players.insert({'name': msg.text})
    await state.clear()
    await msg.answer(text = 'Игрок добавлен', reply_markup=bot_kb.menu_kb())

@r.message(FilterAdmin(Message), F.text == "Удалить игрока")
async def del_player_start(msg: Message, state: FSMContext):
    await state.set_state(bot_states.remove_user.take)
    players = []
    for player in DB.Players.select():
        players.append(player.name)
    await msg.answer(text = 'Выберите игрока', reply_markup=bot_kb.els_kb(players))

@r.message(bot_states.remove_user.take)
async def del_player_finish(msg: Message, state: FSMContext):
    await state.clear()
    if msg.text == 'Главное меню':
        await msg.answer(text = 'Добро пожаловать в меню', reply_markup = bot_kb.menu_kb())
        return
    player = DB.Players.select({'name': msg.text})
    if player == []:
        await msg.answer(text = 'Игрока не найдено', reply_markup = bot_kb.menu_kb())
        return
    DB.Players.delete({'id': player[0].id})
    await msg.answer(text = 'Игрок удалён', reply_markup=bot_kb.menu_kb())