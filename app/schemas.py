from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    token: str

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    profile_image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    variants: List["ProductVariant"] = []
    reviews: List["Review"] = []

    model_config = ConfigDict(from_attributes=True)

class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: datetime
    total: float
    items: List[OrderItem] = []

    model_config = ConfigDict(from_attributes=True)


class Category(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ProductVariant(BaseModel):
    id: int
    name: str
    price: float
    stock: int

    model_config = ConfigDict(from_attributes=True)


class Review(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: int
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromoCode(BaseModel):
    id: int
    code: str
    discount_percent: int
    active: bool

    model_config = ConfigDict(from_attributes=True)


class DeliverySlot(BaseModel):
    id: int
    slot_time: str
    available: bool

    model_config = ConfigDict(from_attributes=True)


Product.model_rebuild()
