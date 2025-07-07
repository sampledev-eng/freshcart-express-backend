from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Enum as SqlEnum, Text
import enum
from sqlalchemy.orm import relationship

from datetime import datetime
from .db import Base

class OrderStatusEnum(enum.Enum):
    PLACED = "placed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    profile_image = Column(String, nullable=True)
    reset_code = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    reviews = relationship('Review', back_populates='user')

    orders = relationship("Order", back_populates="user")

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=0)

    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    category = relationship('Category', back_populates='products')
    variants = relationship('ProductVariant', back_populates='product')
    reviews = relationship('Review', back_populates='product')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    status = Column(SqlEnum(OrderStatusEnum), default=OrderStatusEnum.PLACED)
    created_at = Column(DateTime, default=datetime.utcnow)
    total = Column(Float, default=0)
    delivery_slot_id = Column(Integer, ForeignKey('delivery_slots.id'), nullable=True)
    tracking_number = Column(String, nullable=True)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    delivery_slot = relationship('DeliverySlot', uselist=False, back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    products = relationship('Product', back_populates='category')


class ProductVariant(Base):
    __tablename__ = 'product_variants'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    name = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=0)

    product = relationship('Product', back_populates='variants')


class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship('Product', back_populates='reviews')
    user = relationship('User', back_populates='reviews')


class PromoCode(Base):
    __tablename__ = 'promocodes'
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    discount_percent = Column(Integer, default=0)
    active = Column(Boolean, default=True)


class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DeliverySlot(Base):
    __tablename__ = 'delivery_slots'
    id = Column(Integer, primary_key=True)
    slot_time = Column(String)
    available = Column(Boolean, default=True)

    order_id = Column(Integer, ForeignKey('orders.id'))
    order = relationship('Order', back_populates='delivery_slot')
