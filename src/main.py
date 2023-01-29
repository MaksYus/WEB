from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from starlette.middleware.cors import CORSMiddleware

import datetime
import uvicorn
from typing import List

from src import crud, models, schemas
from src.database import SessionLocal, engine
import json

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def get_user_components(db:Session, user_id:int):
    components = []
    user_roles = crud.get_user_roles(db,user_id)
    for item in user_roles:
        components_id = crud.get_components_id_by_role(db,item.id)
        for comp_id in components_id:
            comp = crud.get_component(db,comp_id.id)
            components.append(comp.name)
    return components


@app.get("/user_all")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получение списка пользователей
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/user_by_id/{user_id}")
def read_user_id(user_id: int, db: Session = Depends(get_db)):
    """
    Получение пользователя по id, если такого id нет, то выдается ошибка
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/user_by_token/{user_token}")
def read_user_token(user_token: str, db: Session = Depends(get_db)):
    """
    Получение пользователя по token
    """
    db_user = crud.get_user_by_token(db, token=user_token)
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
def add_role_for_user(user_login:str, role_name:str,db: Session = Depends(get_db)):
    """
    Добавление роли нужному пользователю
    """
    db_user = crud.get_user_by_login(db, login=user_login)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_role = crud.get_role_by_name(db,name = role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    rfu = schemas.Roles_for_usersBase(user_id = db_user.id, role_id = db_role.id)
    db_role_for_user = crud.create_role_for_user(db,rfu)
    return db_role_for_user

@app.post('/user/auth')
def auth(user: schemas.UserCreate,db: Session = Depends(get_db)):
    """
    авторизация
    """
    hashed_pas = crud.hash_pas(user.password)
    user_db = crud.get_user_by_login(db,user.login)
    if user_db is None:
        raise HTTPException(status_code=400, detail="login or password wrong")
    if user_db.hashed_password != hashed_pas:
        raise HTTPException(status_code=400, detail="login or password wrong")
    if user_db.is_active:
        raise HTTPException(status_code=400, detail="user already logged")
    token = user_db.login + 'FAKETOKEN'
    res = crud.update_user(db,user_db.id,hashed_pas,1,token=token)
    return res

@app.get('/user/unlog/{token}')
def unlog(token:str,db:Session = Depends(get_db)):
    """
    разлогиниться
    """
    user = crud.get_user_by_token(db,token)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found or already logout")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="user already unlogged")
    res = crud.update_user(db,user.id,user.hashed_password,0,user.login)
    return res

@app.post('/user/register')
def register(new_user: schemas.UserCreate, db:Session = Depends(get_db)):
    """
    """
    user = crud.get_user_by_login(login=new_user.login,db=db)
    if not (user is None):
        raise HTTPException(status_code=400, detail='user already exists')
    us = crud.create_user(db=db,user=new_user)
    rol = add_role_for_user(user_login=us.login,role_name='User',db=db)
    return us

@app.get('/candle/all')
def get_all_candles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    candles = crud.get_candles_all(db, skip=skip, limit=limit)
    return candles

@app.post('/candle/create/')
def create_candle(new_candle:schemas.CandlesBase,token:str, db:Session = Depends(get_db)):
    """
    """
    if new_candle.life_time <= 0 :
        raise HTTPException(status_code=400, detail='life time less then 1')
    user_db = crud.get_user(db,new_candle.user_id)
    if user_db is None:
        raise HTTPException(status_code=404, detail='user not found')
    if token != user_db.token:
        raise HTTPException(status_code=400, detail= 'token is unvalid')
    res = crud.create_candle(db=db,ca=new_candle)
    return res

@app.post('/candle/add_to_user/') # сразу зажженная
def add_candle_to_user(new_candle:schemas.CandlesBase,in_user_int:int, db:Session = Depends(get_db)):
    """
    компонент add_candle
    """
    user = crud.get_user(db,new_candle.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')
    #обработка ролевки
    components = get_user_components(db,user.id)
    if ('add_candle' not in components):
        raise HTTPException(status_code=403,detail='deny')
    candle = create_candle(new_candle=new_candle,token=user.token,db=db)
    
    user_candles = crud.get_candles_by_user(db,user.id)
    for candle_intem in user_candles:
        if candle_intem.in_user_interface == in_user_int:
            raise HTTPException(status_code=300, detail='cunt past, older candle must be removed')
    
    if ((in_user_int == 1) and ('one_candle' in components)) or ((in_user_int == 2) and ('two_candle' in components)) or ((in_user_int == 3) and ('three_candle' in components)):
        candle.in_user_interface = in_user_int
        candle.is_burn = 1
        candle.date_start = datetime.datetime.now()
        return crud.update_candle(db,candle)
    raise HTTPException(status_code=403,detail='deny: in user interface')
    

@app.get('/candle/remove/{candle_id}')
def remove_candle(candle_id:int,user_id:int, db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    components = get_user_components(db,user_id)
    if ('rem_candle' not in components):
        raise HTTPException(status_code=403,detail='deny')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')
    ca.life_time = 0
    ca.is_burn = 0
    ca.user_id = -1
    ca.date_start = datetime.datetime.now()
    res = crud.update_candle(db,ca)
    return res

@app.get('/candle/burn/{candle_id}')
def candle_burn(candle_id:int,user_id:int,db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    components = get_user_components(db,user_id)
    if ('burn' not in components):
        raise HTTPException(status_code=403,detail='deny')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')
    ca.is_burn = 1
    ca.date_start = datetime.datetime.now()
    res = crud.update_candle(db,ca)
    return res

@app.get('/candle/unburn/{candle_id}')
def candle_unburn(candle_id:int,user_id:int, db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    components = get_user_components(db,user_id)
    if ('unburn' not in components):
        raise HTTPException(status_code=403,detail='deny')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')
    if ca.is_burn == 0:
        raise HTTPException(status_code=405, detail='candle already unburn')
    ca.is_burn = 0
    delta:datetime.timedelta = (datetime.datetime.now() - ca.date_start)
    ca.life_time -= (delta.days*24*3600 + delta.seconds)
    res = crud.update_candle(db,ca)
    return res

@app.get('/candle/get_on_pos_in_user')
def get_candle_in_user_pos(candle_in_user_interface:int, user_id:int,  db:Session = Depends(get_db)):
    user_candles = crud.get_candles_by_user(db,user_id)
    if user_candles is None:
        raise HTTPException(status_code=404, detail='candles not found')
    for candle_intem in user_candles:
        if candle_intem.in_user_interface == candle_in_user_interface:
            return candle_intem
    raise HTTPException(status_code=404, detail='candles not found')