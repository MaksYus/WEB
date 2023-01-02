from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

class BaseModel(Base):
    """
    Абстартный базовый класс, где описаны все поля и методы по умолчанию
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True,unique=True)

    def __repr__(self):
        return f"<{type(self).__name__}(id={self.id})>"

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    is_active = Column(Boolean, default=True,nullable=False)

class History(BaseModel):
    __tablename__ = "history"

    date = Column(Date)
    fild_name = Column(String)
    old_val = Column(String)
    new_val = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)

class Candles(BaseModel):
    __tablename__ = "candles"

    life_time = Column(Integer,nullable=False)
    is_burn = Column(Boolean, default=True,nullable=False)
    date_start = Column(Date)

    candle_type_id = Column(Integer, ForeignKey("candle_type.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

class Candle_Type(BaseModel):
    __tablename__ = "candle_type"

    canlde_type = Column(String, index = True,unique=True,nullable=False)
    path = Column(String)

class Role(BaseModel):
    __tablename__ = "role"

    name = Column(String, index = True,unique=True,nullable=False)

class Component(BaseModel):
    __tablename__ = "component"

    name = Column(String, index = True,unique=True,nullable=False)

class Roles_for_users(BaseModel):
    __tablename__ = "roles_for_users"

    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("role.id"))

class Role_Access(BaseModel):
    __tablename__ = "role_access"

    role_id = Column(Integer,ForeignKey("role.id"),nullable=False)
    component_id = Column(Integer,ForeignKey("component.id"),nullable=False)
