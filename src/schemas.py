from pydantic import BaseModel
from typing import Union, List
import datetime

class BaseIDModel(BaseModel):
    id:int

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    """
    Класс для создания User. Пароль мы не должны нигде отображать, поэтому
    это поле есть только в классе для создания.
    """
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class History(BaseIDModel):
    date: datetime.datetime
    fild_name: str
    old_val: str
    new_val: str
    user_id: int

class Candles(BaseIDModel):
    life_time: int
    is_burn: bool
    date_start: datetime.datetime
    candle_type_id: int
    user_id: int

class Candle_Type(BaseIDModel):
    candle_type: str
    path: str

class Role(BaseIDModel):
    name: str

class Component(BaseIDModel):
    name: str

class Roles_for_users(BaseIDModel):
    user_id: int
    role_id: int

class Role_Access(BaseIDModel):
    role_id: int
    component_id: int
