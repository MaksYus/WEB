from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()

class BaseModel(Base):
    """
    Абстартный базовый класс, где описаны все поля и методы по умолчанию
    """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True,unique=True)

    def to_dict(self) -> dict:
        return {'id': self.id}

    def __repr__(self):
        return f"<{type(self).__name__}(id={self.id})>"

class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    is_active = Column(Boolean, default=False,nullable=False)

    def to_dict(self) -> dict:
        return {'id': self.id,'email': self.email, 'hashed_password': self.hashed_password, 'is_active':self.is_active}

class History(BaseModel):
    __tablename__ = "history"

    date = Column(DateTime)
    fild_name = Column(String)
    old_val = Column(String)
    new_val = Column(String)

    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)

    def to_dict(self) -> dict:
        return {'id': self.id,'date': self.date, 'fild_name': self.fild_name, 'old_val':self.old_val, 'new_val':self.new_val, 'user_id':self.user_id}


class Candles(BaseModel):
    __tablename__ = "candles"

    life_time = Column(Integer,nullable=False)
    is_burn = Column(Boolean, default=False,nullable=False)
    date_start = Column(DateTime)

    candle_type_id = Column(Integer, ForeignKey("candle_type.id"),nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))

    def to_dict(self) -> dict:
        return {'id': self.id,'life_time': self.life_time, 'is_burn': self.is_burn, 'date_start':self.date_start, 'candle_type_id':self.candle_type_id, 'user_id':self.user_id}

class Candle_Type(BaseModel):
    __tablename__ = "candle_type"

    canlde_type = Column(String, index = True,unique=True,nullable=False)
    path = Column(String)

    def to_dict(self) -> dict:
        return {'id': self.id,'canlde_type': self.canlde_type, 'path': self.path}

class Role(BaseModel):
    __tablename__ = "role"

    name = Column(String, index = True,unique=True,nullable=False)

    def to_dict(self) -> dict:
        return {'id': self.id,'name': self.name}

class Component(BaseModel):
    __tablename__ = "component"

    name = Column(String, index = True,unique=True,nullable=False)
    def to_dict(self) -> dict:
        return {'id': self.id,'name': self.name}

class Roles_for_users(BaseModel):
    __tablename__ = "roles_for_users"

    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("role.id"))

    def to_dict(self) -> dict:
        return {'id': self.id,'user_id': self.user_id, 'role_id': self.role_id}

class Role_Access(BaseModel):
    __tablename__ = "role_access"

    role_id = Column(Integer,ForeignKey("role.id"),nullable=False)
    component_id = Column(Integer,ForeignKey("component.id"),nullable=False)
    def to_dict(self) -> dict:
        return {'id': self.id,'role_id': self.role_id, 'component_id': self.component_id}
