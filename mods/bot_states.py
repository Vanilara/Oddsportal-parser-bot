from aiogram.fsm.state import State, StatesGroup


class add_user(StatesGroup):
    take = State()

class remove_user(StatesGroup):
    take = State()

class filter_setts(StatesGroup):
    player = State()
    type_action = State()
    keyword_add = State()
    keyword_del = State()