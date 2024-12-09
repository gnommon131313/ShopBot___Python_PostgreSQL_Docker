import telebot
from telebot import types, SimpleCustomFilter, AdvancedCustomFilter
from telebot.callback_data import CallbackData, CallbackDataFilter
import os


chapter_load = CallbackData('chapter', 'page', prefix='prefix_chapter_load')
product_card_load = CallbackData('id', prefix='prefix_product_card_load')
db_insert = CallbackData('table', 'parameters', prefix='prefix_db_insert')
db_delete = CallbackData('table', 'parameters', prefix='prefix_db_delete')
db_update = CallbackData('table', 'parameters', prefix='prefix_db_update')

def bind(bot: telebot.TeleBot):
    bot.add_custom_filter(AdminFilter())
    bot.add_custom_filter(CallbackFilter())


class AdminFilter(SimpleCustomFilter):
    key = 'admin'

    def check(self, message):
        # Нужно преобразовать, os.getenv возвращает str
        admin = os.getenv("ADMIN").split(', ')
        admin = [int(x) for x in admin]
        
        return message.from_user.id in admin


class CallbackFilter(AdvancedCustomFilter):
    key = 'callback_config'

    def check(self, call: types.CallbackQuery, callback_filter: CallbackDataFilter):
        return callback_filter.check(query=call)