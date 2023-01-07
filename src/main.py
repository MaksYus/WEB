from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import datetime
import uvicorn
from typing import List

from src import crud, models, schemas
from src.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0', port=8000) # pragma: no cover

# Dependency
def get_db():
    """
    Задаем зависимость к БД. При каждом запросе будет создаваться новое
    подключение.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Создание пользователя
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка пользователей
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Получение пользователя по id, если такого id нет, то выдается ошибка
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get('/roles/{user_id}')
def read_role_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    получить роли для пользователя
    """
    db_role = crud.get_user_roles(db,user_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="role for user not found")
    return db_role

@app.post('/roles/')
def add_role_for_user(user_email:str, role_name:str,db: Session = Depends(get_db)):
    """
    Добавление роли нужному пользователю
    """
    db_user = crud.get_user_by_email(db, email=user_email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_role = crud.get_role_by_name(db,name = role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    rfu = schemas.Roles_for_usersBase(user_id = db_user.id, role_id = db_role.id)
    db_role_for_user = crud.create_role_for_user(db,rfu)
    return db_role_for_user

@app.post('/user/auth/')
def auth(email:str, password:str,db: Session = Depends(get_db)):
    """
    авторизация
    """
    hashed_pas = crud.hash_pas(password)
    user = crud.get_user_by_email(db,email)
    if user is None:
        raise HTTPException(status_code=400, detail="login or password wrong")
    if user.hashed_password != hashed_pas:
        raise HTTPException(status_code=400, detail="login or password wrong")
    if user.is_active:
        raise HTTPException(status_code=400, detail="user already logged")
    res = crud.update_user(db,user.id,hashed_pas,1)

@app.post('/user/unlog/')
def unlog(email:str,db:Session = Depends(get_db)):
    """
    разлогиниться
    """
    user = crud.get_user_by_email(db,email)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="user already unlogged")
    res = crud.update_user(db,user.id,user.hashed_password,0)

@app.post('/user/register/')
def register(new_user: schemas.UserCreate, db:Session = Depends(get_db)):
    """
    """
    user = crud.get_user_by_email(email=new_user.email,db=db)
    if not (user is None):
        raise HTTPException(status_code=400, detail='user already exists')
    us = crud.create_user(db=db,user=new_user)
    rol = add_role_for_user(user_email=us.email,role_name='User',db=db)
    return us

@app.post('/candle/add/')
def add_candle(new_candle:schemas.CandlesBase, db:Session = Depends(get_db)):
    """
    """
    if new_candle.life_time <= 0 :
        raise HTTPException(status_code=400, detail='life time less then 1')
    user_db = crud.get_user(db,new_candle.user_id)
    if user_db is None:
        raise HTTPException(status_code=404, detail='user not found')
    res = crud.create_candle(db=db,ca=new_candle)
    return res

@app.post('/candle/remove/')
def remove_candle(candle_id:int , db:Session = Depends(get_db)):
    """
    """
    ca = crud.get_candle(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')
    ca.life_time = 0
    ca.is_burn = 0
    ca.user_id = -1
    ca.date_start = datetime.datetime.now()
    res = crud.update_candle(db,ca)
    return res

# авторизация
# регистрация
# добавление роли
# создание всего
# поставить/убрать свечку
# затушить/зажеч 