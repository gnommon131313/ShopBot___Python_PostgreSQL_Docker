import os, logging
from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from app.database import init_db
from app.handlers import admin, shop, database, user
from app.utils import filters, states


state_storage = StateMemoryStorage()
bot = TeleBot(os.getenv("BOT_TOKEN"), state_storage=state_storage, num_threads=5)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

init_db.init()

def register_handlers():
    shop_ = shop.Shop()
    user_ = user.User()

    def admin_handler() -> None:
        bot.register_message_handler(admin.some_start, commands=['debug'], admin=True, pass_bot=True)

    def app_handler() -> None:
        bot.register_message_handler(shop_.start, commands=['start'], pass_bot=True)
        bot.register_callback_query_handler(
            shop_.menu_load_with_call, func=lambda call: call.data == 'menu_load', pass_bot=True)
        bot.register_callback_query_handler(
            shop_.chapter_load, func=None, callback_config=filters.chapter_load.filter(), pass_bot=True)
        bot.register_callback_query_handler(
            shop_.product_card_load, func=None, callback_config=filters.product_card_load.filter(), pass_bot=True)

    def database_handler() -> None:
        bot.register_callback_query_handler(
            database.insert, func=None, callback_config=filters.db_insert.filter(), pass_bot=True)
        bot.register_callback_query_handler(
            database.delete, func=None, callback_config=filters.db_delete.filter(), pass_bot=True)
        bot.register_callback_query_handler(
            database.update, func=None, callback_config=filters.db_update.filter(), pass_bot=True)

    def user_handler() -> None:
        bot.register_message_handler(user_.cancel, commands=['cancel'], admin=False, pass_bot=True)
        bot.register_callback_query_handler(
            user_.make_an_order, func=lambda call: call.data == 'make_an_order', pass_bot=True)
        bot.register_message_handler(
            user_.get_name,
            func=lambda message: bot.get_state(message.from_user.id) == states.User.get_name.name,
            admin=False, pass_bot=True)
        bot.register_message_handler(
            user_.get_phone,
            func=lambda message: bot.get_state(message.from_user.id) == states.User.get_phone.name,
            admin=False, pass_bot=True)
        bot.register_message_handler(
            user_.get_address,
            func=lambda message: bot.get_state(message.from_user.id) == states.User.get_address.name,
            admin=False, pass_bot=True)

    admin_handler()
    app_handler()
    database_handler()
    user_handler()

register_handlers()
filters.bind(bot)
bot.infinity_polling()