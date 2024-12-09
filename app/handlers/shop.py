from telebot import TeleBot
from telebot import types
from app.utils import filters
import math
from app.utils import  buttons
from app.database.engine import SessionLocal
from app.database import models


class Shop:
    def __init__(self) -> None:
        self.__keyboard = types.InlineKeyboardMarkup()
        self.__chapter = ''
        self.__page = 0
        self.__page_capacity = 5
    
    def start(self, message: types.Message, bot: TeleBot) -> None:
        self.menu_load(message=message, bot=bot)
        
        def create_user_staff() -> None:
            with SessionLocal() as session: 
                if session.query(models.User).filter_by(id=message.from_user.id).first():
                    return
                
                user = models.User(id=message.from_user.id, name=message.from_user.first_name)
                basket = models.Basket(user=user)
                
                session.add(user)
                session.add(basket)
                session.commit()
    
        create_user_staff()
    
    def menu_load(self, message: types.Message, bot: TeleBot) -> None:
        def create_keyboard() -> None:
            self.__keyboard = types.InlineKeyboardMarkup()
            self.__keyboard.row(
                buttons.chapter('catalog',0),
                buttons.chapter('basket',0),)

        def edit_message() -> None:
            if message.text:
                if "/" in message.text:
                    bot.send_message(message.chat.id, text="menu:", reply_markup=self.__keyboard)
                else:
                    # Команды нельзя отредактировать (+бот может редактировать только свои собственные сообщения)
                    bot.edit_message_text(text="menu:", chat_id=message.chat.id, message_id=message.message_id,
                                      reply_markup=self.__keyboard)
            elif message.photo:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.send_message(message.chat.id, text="menu:", reply_markup=self.__keyboard)

        create_keyboard()
        edit_message()

    def menu_load_with_call(self, call: types.CallbackQuery, bot: TeleBot) -> None:
        self.menu_load(message=call.message, bot=bot)

    def chapter_load(self, call: types.CallbackQuery, bot: TeleBot) -> None:
        callback_data: dict = filters.chapter_load.parse(callback_data=call.data)
        self.__chapter = callback_data['chapter']
        self.__page = int(callback_data['page'])
        products = []

        if self.__chapter == 'catalog':
            with SessionLocal() as session:
                products = session.query(models.Product).all()

        elif self.__chapter == 'basket':
            with SessionLocal() as session: 
                basket = session.query(models.Basket).filter_by(user_id=call.from_user.id).first()
                products_in_basket = session.query(models.BasketProduct).filter_by(basket_id=basket.id).all()
                
                for element in products_in_basket:
                    products.append(element.product)
                    
        def create_keyboard() -> None:
            page_max = math.floor(len(products) / self.__page_capacity)

            self.__keyboard = types.InlineKeyboardMarkup()
            self.__keyboard.row(*buttons.products(products, self.__page, self.__page_capacity))
            self.__keyboard.row(
                buttons.page_switcher(self.__chapter, self.__page, page_max, -1),
                buttons.info(callback_data['page']),
                buttons.page_switcher(self.__chapter, self.__page, page_max, +1))

            if self.__chapter == 'basket' and len(products) > 0:
                    self.__keyboard.row(buttons.make_an_order())

            self.__keyboard.row(buttons.menu())

        def edit_message() -> None:
            if call.message.text:
                bot.edit_message_text(text=f"{callback_data['chapter']}:", chat_id=call.message.chat.id,
                                      message_id=call.message.id)
                bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=self.__keyboard)

            elif call.message.photo:
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                bot.send_message(call.message.chat.id, text=f"{callback_data['chapter']}:", reply_markup=self.__keyboard)

        create_keyboard()
        edit_message()

    def product_card_load(self, call: types.CallbackQuery, bot: TeleBot) -> None:
        callback_data: dict = filters.product_card_load.parse(callback_data=call.data)
        
        with SessionLocal() as session: 
            product = session.query(models.Product).filter_by(id=callback_data['id']).first()

        def create_keyboard() -> None:
            self.__keyboard = buttons.basket_staff(product_id=product.id, user_id=call.from_user.id)
            self.__keyboard.row(buttons.chapter(self.__chapter, self.__page))

        def edit_message() -> None:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            with open(product.image_path, 'rb') as photo:
                bot.send_photo(chat_id=call.message.chat.id, photo=photo,
                    caption=f"{product.name}  =  {product.price}$",
                    reply_markup=self.__keyboard)

        create_keyboard()
        edit_message()