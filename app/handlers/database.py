from telebot import TeleBot
from telebot import types
from app.utils import filters
from app.database.engine import SessionLocal
from app.database import models
import numpy
from app.utils import  buttons


def insert(call: types.CallbackQuery, bot: TeleBot) -> None:
    callback_data: dict = filters.db_insert.parse(callback_data=call.data)
    parameters = callback_data['parameters'].split(", ")  # Превратит в список в любом случае

    if callback_data['table'] == 'basket_products':
        with SessionLocal() as session: 
            session.add(models.BasketProduct(basket_id=parameters[0], product_id=parameters[1], quantity=parameters[2]))
            session.commit()

    def edit_message() -> None:
        keyboard = buttons.basket_staff(product_id=parameters[1], user_id=call.from_user.id)
        keyboard.row(buttons.menu())
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)

    edit_message()

def delete(call: types.CallbackQuery, bot: TeleBot) -> None:
    callback_data: dict = filters.db_delete.parse(callback_data=call.data)
    parameters = callback_data['parameters'].split(", ")

    if callback_data['table'] == 'basket_products':
        with SessionLocal() as session: 
            row = session.query(models.BasketProduct).filter_by(basket_id=parameters[0], product_id=parameters[1]).first()
            
            if row is None:
                return
            
            session.delete(row)
            session.commit()
            
    def edit_message() -> None:
        keyboard = buttons.basket_staff(product_id=parameters[0], user_id=call.from_user.id)
        keyboard.row(buttons.menu())
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)

    edit_message()

def update(call: types.CallbackQuery, bot: TeleBot) -> None:
    callback_data: dict = filters.db_update.parse(callback_data=call.data)
    parameters = callback_data['parameters'].split(", ")
    edit_message = False  # Защита от исключения
    
    if callback_data['table'] == 'basket_products':
        with SessionLocal() as session:
            product_in_basket = session.query(models.BasketProduct).filter_by(basket_id=parameters[0], product_id=parameters[1]).first()

            addend = int(parameters[2])
            summ = int(numpy.clip(int(product_in_basket.quantity) + addend, 1, 10))

            if product_in_basket.quantity != summ:  
                edit_message = True
                
            product_in_basket.quantity = summ
            session.commit()
                
    if edit_message:
        keyboard = buttons.basket_staff(product_id=parameters[1], user_id=call.from_user.id)
        keyboard.row(buttons.menu())
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)
