from sqlalchemy import Table, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    address = Column(String)

    baskets = relationship("Basket", back_populates="user")
    orders = relationship("Order", back_populates="user")


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, default="super thing")
    price = Column(String, nullable=False)
    image_path = Column(String, nullable=False)

    basket_products = relationship('BasketProduct', back_populates='product')
    order_products = relationship('OrderProduct', back_populates='product')


class Basket(Base):
    __tablename__ = 'baskets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))

    user = relationship('User', back_populates='baskets')
    products = relationship('BasketProduct', back_populates='basket')
    
    def get_product(self):
        return self.products[1]


class BasketProduct(Base):
    __tablename__ = 'basket_products'
    
    basket_id = Column(Integer, ForeignKey('baskets.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer, default=1)

    basket = relationship('Basket', back_populates='products')
    product = relationship('Product', back_populates='basket_products')

    
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    status = Column(String, default='pending')
    date = Column(String)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='orders')
    products = relationship('OrderProduct', back_populates='order')

    
class OrderProduct(Base):
    __tablename__ = 'order_products'
    
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    quantity = Column(Integer, default=1)

    order = relationship('Order', back_populates='products')
    product = relationship('Product', back_populates='order_products')

    
def create_tables(engine) -> None:
    Base.metadata.create_all(bind=engine)