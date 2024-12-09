from telebot.handler_backends import State, StatesGroup


class User(StatesGroup):
    get_name = State()
    get_phone = State()
    get_address = State()