from sqlalchemy.orm import Session

from src import models, schemas

#       USER

def create_user(db: Session, user: schemas.UserCreate):
    """
    Добавление нового пользователя
    """
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    """
    Получить пользователя по его id
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """
    Получить пользователя по его email
    """
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Получить список пользователей из БД
    skip - сколько записей пропустить
    limit - маскимальное количество записей
    """
    return db.query(models.User).offset(skip).limit(limit).all()

#       ROLES

def create_role(db: Session, role: schemas.Role):
    db_role = models.Role(id=role.id,name=role.name)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def create_role_for_user(db:Session, rfu:schemas.Roles_for_users):
    db_r = models.Roles_for_users(id=rfu.id,user_id=rfu.user_id,role_id=rfu.role_id)
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r

def create_role_access(db:Session,ra:schemas.Role_Access):
    db_r = models.Role_Access(id=ra.id,component_id=ra.component_id,role_id=ra.role_id)
    db.add(db_r)
    db.commit()
    db.refresh(db_r)
    return db_r