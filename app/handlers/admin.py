from telebot import TeleBot
from telebot.types import Message


def some_start(self, message: Message, bot: TeleBot) -> None:
    bot.send_message(message.chat.id, text="Hello, admin!")