from telebot import TeleBot
from telebot import types
from app.utils import states
from app.database.engine import SessionLocal
from app.database import models
import json


class User:
    def __init__(self) -> None:
        pass

    def cancel(self, message: types.Message, bot: TeleBot):
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, text="Ваша информация была очищена")
        bot.send_message(message.chat.id, text="/start чтобы начать")

    def make_an_order(self, call: types.CallbackQuery, bot: TeleBot) -> None:
        try:
            # Проверить есть ли товары в корзине
            pass
        except ValueError:
            bot.send_message(chat_id=call.message.chat.id, text="Error")
            return

        bot.set_state(call.from_user.id, states.User.get_name, call.message.chat.id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text="Для оформления заказа введите свои данные: \n/cancel - чтобы отменить")
        bot.send_message(chat_id=call.message.chat.id, text="Укажите Имя")

    def get_name(self, message: types.Message, bot: TeleBot):
        try:
            # Валидация
            pass
        except ValueError:
            bot.send_message(message.chat.id, text="Укажите корректное имя")
            return

        with SessionLocal() as session: 
            user = session.query(models.User).filter_by(id=message.from_user.id).first()
            user.name = message.text
            session.commit()

        bot.set_state(message.from_user.id, states.User.get_phone, message.chat.id)
        bot.send_message(message.chat.id, text="Укажите номер телефона")

    def get_phone(self, message: types.Message, bot: TeleBot):
        try:
            # Валидация
            pass
        except ValueError:
            bot.send_message(message.chat.id, text="Укажите корректный номер телефона")
            return

        with SessionLocal() as session: 
            user = session.query(models.User).filter_by(id=message.from_user.id).first()
            user.phone = message.text
            session.commit()

        bot.set_state(message.from_user.id, states.User.get_address, message.chat.id)
        bot.send_message(message.chat.id, text="Укажите адрес")

    def get_address(self, message: types.Message, bot: TeleBot):
        try:
            # Валидация
            pass
        except ValueError:
            bot.send_message(message.chat.id, text="Укажите корректный адрес")
            return

        bot.send_message(chat_id=message.chat.id, text="Заказ успешно оформлен!")
        bot.delete_state(message.from_user.id, message.chat.id)
        
        def order_finished() -> None:
            with SessionLocal() as session: 
                user = session.query(models.User).filter_by(id=message.from_user.id).first()
                user.address = message.text

                # Достать из корзины
                basket = session.query(models.Basket).filter_by(user_id=message.from_user.id).first()
                products_in_basket = session.query(models.BasketProduct).filter_by(
                    basket=basket).all()
                
                # Создать заказ
                order = models.Order(date='today', user=user)
                session.add(order)
                
                # Поместить продукты под заказ
                for element in products_in_basket:
                    products_in_order = models.OrderProduct(
                        order=order, product=element.product, quantity=element.quantity)
                    session.add(products_in_order)
                
                # Удалить из корзины
                for element in products_in_basket:
                    session.delete(element)
                
                session.commit()
                
            def save_on_json() -> None:
                with SessionLocal() as session: 
                    orders = session.query(models.Order).all()
                
                def order_to_dict(order) -> dict:
                    return {
                        "id": order.id,
                        "status": order.status,
                        "date": order.date,
                        "user_id": order.user_id
                    }

                orders_dict = [order_to_dict(order) for order in orders]
                orders_json = json.dumps(orders_dict, ensure_ascii=False, indent=4)
                    
                with open('order.json', 'w', encoding='utf-8') as file_w:
                    file_w.write(orders_json)

            save_on_json()
        order_finished()