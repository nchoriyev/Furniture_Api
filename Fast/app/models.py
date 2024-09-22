from .database import Base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, func, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum


class Country(Base):
    __tablename__ = 'country'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Relationship to City and Product
    cities = relationship('City', back_populates='country_relation')
    products = relationship('Product', back_populates='country_relation')


class City(Base):
    __tablename__ = 'city'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    country_id = Column(ForeignKey('country.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    country_relation = relationship('Country', back_populates='cities')
    addresses = relationship('Address', back_populates='city_relation')


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    city_id = Column(ForeignKey('city.id'), nullable=False)
    country_id = Column(ForeignKey('country.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    city_relation = relationship('City', back_populates='addresses')
    country_relation = relationship('Country')


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(Text)
    material = Column(String)
    price1 = Column(Float)
    price2 = Column(Float)
    status = Column(Boolean, default=True)
    featured = Column(Boolean, default=False)
    country_id = Column(ForeignKey('country.id'), nullable=False)
    count = Column(Integer)
    slug = Column(String)
    created_at = Column(DateTime(timezone=True))

    country_relation = relationship('Country', back_populates='products')


class UserStatus(enum.Enum):
    USER = "user"
    ADMIN = "admin"
    DELIVER = "deliver"


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(30), nullable=False)
    last_name = Column(String(30), nullable=False)
    username = Column(String(30), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ADMIN)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    orders = relationship('Order', back_populates='user_relation')
    deliveries = relationship('Delivery', back_populates='user_relation')


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    product_id = Column(ForeignKey('product.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=func.now())

    user_relation = relationship('User', back_populates='orders')
    product_relation = relationship('Product')


class StatusDelivery(enum.Enum):
    PENDING = "pending"
    DELIVERED = "delivered"


class Delivery(Base):
    __tablename__ = 'delivery'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    order_id = Column(ForeignKey('order.id'), nullable=False)
    status = Column(Enum(StatusDelivery), default=UserStatus.USER)

    user_relation = relationship('User', back_populates='deliveries')
    order_relation = relationship('Order')


class Contact(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True, autoincrement=True)  # Add a primary key
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    email = Column(String(50), nullable=False)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=func.now())
