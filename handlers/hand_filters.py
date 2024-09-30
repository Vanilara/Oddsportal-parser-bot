from aiogram import Router, F
from aiogram.types import Message
from aiogram import F
from aiogram.fsm.context import FSMContext
from database import DB
from mods import bot_kb, bot_states

r = Router()

async def player_info(state, msg, player, player_id):
    await state.update_data(player_id=player_id)
    await state.update_data(player=player)
    await state.set_state(bot_states.filter_setts.type_action)
    message = f'Фильтры для {player}:\n'
    for filter in DB.Filters.select({'player_id': player_id}):
        if filter.is_positive == 0:
            message += f'{filter.type} - !{filter.keyword}\n'
        else:
            message += f'{filter.type} - {filter.keyword}\n'
    await msg.answer(text = message, reply_markup=bot_kb.filter_actions())


@r.message(bot_states.filter_setts.player)
async def show_player_filters(msg: Message, state: FSMContext):
    player_id = DB.Players.select({'name': msg.text})[0].id
    player = msg.text
    await player_info(state, msg, player, player_id)
    

@r.message(bot_states.filter_setts.type_action)
async def choose_type(msg: Message, state: FSMContext):
    action = msg.text.split('|')[1].strip()
    await state.update_data(type=msg.text.split('|')[0].strip())
    data = await state.get_data()
    if action == 'добавить':
        await state.set_state(bot_states.filter_setts.keyword_add)
        message = f'Отправьте название как в oddsportal. Для установки фильтра "кроме" используйте ! перед названием (!Football)'
        await msg.answer(text = message, reply_markup=bot_kb.back_kb())
    elif action == 'удалить':
        await state.set_state(bot_states.filter_setts.keyword_del)
        message = f'Выберите один из фильтров с клавиатуры'
        keywords = []
        for keyword in DB.Filters.select({'player_id': data['player_id'], 'type': data['type']}):
            if keyword.is_positive == 0:
                keywords.append('!' + keyword.keyword)
            else:
                keywords.append(keyword.keyword)
        await msg.answer(text = message, reply_markup=bot_kb.els_kb(keywords))

@r.message(bot_states.filter_setts.keyword_add)
async def add_keyword(msg: Message, state: FSMContext):
    keyword = msg.text
    if keyword[0] == '!':
        is_positive = False
        keyword = keyword[1:]
    else:
        is_positive = True
    data = await state.get_data()
    DB.Filters.insert({'type': data['type'], 'player_id': data['player_id'], 'keyword': keyword, 'is_positive': is_positive})
    message = 'Добавлено'
    await msg.answer(text = message, reply_markup=bot_kb.back_kb())
    await player_info(state, msg, data['player'], data['player_id'])


@r.message(bot_states.filter_setts.keyword_del)
async def del_keyword(msg: Message, state: FSMContext):
    keyword = msg.text
    data = await state.get_data()
    if keyword[0] == '!':
        is_positive = False
        keyword = keyword[1:]
    else:
        is_positive = True
    DB.Filters.delete({'type': data['type'], 'player_id': data['player_id'], 'keyword': keyword, 'is_positive': is_positive})
    message = 'Удалено'
    await msg.answer(text = message, reply_markup=bot_kb.back_kb())
    await player_info(state, msg, data['player'], data['player_id'])