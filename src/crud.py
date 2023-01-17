from sqlalchemy.orm import Session
from sqlalchemy import insert

from src import models, schemas

def get_f(item):
    if item :
        return item.to_dict()
    else: return {}

def hash_pas(password:str):
    return password + "notreallyhashed"

#       USER

def create_user(db: Session, user: schemas.UserCreate):
    """
    Добавление нового пользователя
    """
    fake_hashed_password = hash_pas(user.password)
    db_user = models.User(login=user.login, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """
    Получить пользователя по его id
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_login(db: Session, login: str):
    """
    Получить пользователя по его login
    """
    return db.query(models.User).filter(models.User.login == login).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Получить список пользователей из БД
    skip - сколько записей пропустить
    limit - маскимальное количество записей
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db:Session,id:int, h_password:str, is_active:int, token:str):
    user = get_user(db,id)
    user.hashed_password = h_password
    user.is_active = is_active
    user.token = token
    db.commit()
    db.refresh(user)
    return user
#       ROLES

def create_role(db: Session, role: schemas.RoleBase):
    db_role = models.Role(name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_role_for_user(db:Session, rfu:schemas.Roles_for_usersBase):
    db_r = models.Roles_for_users(user_id=rfu.user_id,role_id=rfu.role_id)
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r

def create_role_access(db:Session,ra:schemas.Role_AccessBase):
    db_r = models.Role_Access(component_id=ra.component_id,role_id=ra.role_id)
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r

def get_role_by_id(db:Session, id_role:int):
    return db.query(models.Role).filter(models.Role.id == id_role).first()

def get_role_by_name(db:Session, name:str):
    return db.query(models.Role).filter(models.Role.name == name).first()

def get_user_roles(db:Session, id_user:int):
    return db.query(models.Roles_for_users).filter(models.Roles_for_users.user_id == id_user).all()

#           CANDLES

def create_candle(db:Session, ca:schemas.CandlesBase):
    db_r = models.Candles(life_time = ca.life_time, candle_type_id = ca.candle_type_id,user_id = ca.user_id)
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r

def get_candle(db:Session, ca_id: int):
    return db.query(models.Candles).filter(models.Candles.id == ca_id).first()

def update_candle(db:Session,ca: models.Candles):
    db.commit()
    db.refresh(ca)
    return ca