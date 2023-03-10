from pydantic import BaseModel
from typing import Union, List
import datetime

class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    """
    Класс для создания User. Пароль мы не должны нигде отображать, поэтому
    это поле есть только в классе для создания.
    """
    password: str


class User(UserBase):
    id: int
    is_active: bool
    token: str
    class Config:
        orm_mode = True

class HistoryBase(BaseModel): #для создания использовать этот
    date_changes: datetime.datetime
    fild_name: str
    old_val: str
    new_val: str
    description: str

class History(HistoryBase):
    id: int
    class Config:
        orm_mode = True

class CandlesBase(BaseModel): #для создания использовать этот
    life_time: int
    candle_type_id: int
    user_id: int

class Candles(CandlesBase):
    is_burn: bool
    date_start: datetime.datetime
    id: int
    in_user_interface: int
    class Config:
        orm_mode = True

class CandleTypeBase(BaseModel):
    candle_type: str
    path: str

class Candle_Type(CandleTypeBase):
    id: int
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str

class Role(RoleBase):
    id: int
    class Config:
        orm_mode = True

class ComponentBase(BaseModel):
    name: str

class Component(ComponentBase):
    id: int
    class Config:
        orm_mode = True

class Roles_for_usersBase(BaseModel):
    user_id: int
    role_id: int

class Roles_for_users(Roles_for_usersBase):
    id: int
    class Config:
        orm_mode = True

class Role_AccessBase(BaseModel):
    role_id: int
    component_id: int

class Role_Access(Role_AccessBase):
    id: int
    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    text: str
    user_id: int

class Message(MessageBase):
    id: int
    date: datetime.datetime
    class Config:
        orm_mode = True