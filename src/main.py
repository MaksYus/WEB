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

    history = schemas.HistoryBase(
        date_changes = datetime.datetime.now(),
        fild_name='roles_for_users.id roles_for_users.user_id roles_for_users.role_id',
        old_val='',
        new_val=str(db_role_for_user.id)+' '+str(db_role_for_user.user_id)+' '+str(db_role_for_user.role_id),
        description='adding role to user')
    histor = crud.create_history(db,history)

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

    history = schemas.HistoryBase(
        date_changes = datetime.datetime.now(),
        fild_name='users.is_active users.token',
        old_val=str(user_db.is_active)+' '+user_db.token,
        new_val='1 '+token,
        description='user '+ user_db.login +' log in')
    
    res = crud.update_user(db,user_db.id,hashed_pas,1,token=token)
    histor = crud.create_history(db,history)
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

    history = schemas.HistoryBase(
        date_changes = datetime.datetime.now(),
        fild_name='users.is_active users.token',
        old_val=str(user.is_active)+' '+user.token,
        new_val='0 '+token,
        description='user '+ user.login +' log out')
    histor = crud.create_history(db,history)

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

    history = schemas.HistoryBase(
        date_changes = datetime.datetime.now(),
        fild_name='users.id users.login users.hashed_password users.is_active users.token',
        old_val='',
        new_val=str(us.id)+' '+us.login+' '+us.hashed_password+' '+str(us.is_active)+' '+us.token,
        description='user '+ us.login +' registered')

    rol = add_role_for_user(user_login=us.login,role_name='User',db=db)
    histor = crud.create_history(db,history)
    return us

@app.get('/user/components/{id}')
def get_components(id:int, db:Session = Depends(get_db)):
    return {'components': get_user_components(db,id)}

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

    history = schemas.HistoryBase(
        date_changes = datetime.datetime.now(),
        fild_name='candles.id candles.life_time candles.is_burn candles.date_start candles.candle_type_id candles.user_id candles.in_user_inreface',
        old_val='',
        new_val=str(res.id)+' '+str(res.life_time)+' '+str(res.is_burn)+' '+str(res.date_start)+' '+str(res.candle_type_id)+' '+str(res.user_id)+' '+str(res.in_user_interface),
        description='user '+ user_db.login +' create new candle id:'+str(res.id))
    histor = crud.create_history(db,history)

    return res

@app.post('/candle/add_to_user/') # сразу зажженная
def add_candle_to_user(new_candle:schemas.CandlesBase,components:list,in_user_int:int, db:Session = Depends(get_db)):
    """
    компонент add_candle
    """
    user = crud.get_user(db,new_candle.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail='user not found')
    #обработка ролевки
    if ('add_candle' not in components):
        raise HTTPException(status_code=403,detail='deny: role access')
    candle = create_candle(new_candle=new_candle,token=user.token,db=db)
    
    user_candles = crud.get_candles_by_user(db,user.id)
    for candle_intem in user_candles:
        if candle_intem.in_user_interface == in_user_int:
            raise HTTPException(status_code=300, detail='cunt past, older candle must be removed')
    
    if ((in_user_int == 1) and ('one_candle' in components)) or ((in_user_int == 2) and ('two_candle' in components)) or ((in_user_int == 3) and ('three_candle' in components)):
        date_now = datetime.datetime.now()
        history = schemas.HistoryBase(
            date_changes = date_now,
            fild_name='candles.in_user_interface candles.is_burn candles.date_start',
            old_val=str(candle.in_user_interface)+' '+str(candle.is_burn)+' '+str(candle.date_start),
            new_val=str(in_user_int)+' 1 '+str(date_now),
            description='adding candle to user')
        histor = crud.create_history(db,history)

        candle.in_user_interface = in_user_int
        candle.is_burn = 1
        candle.date_start = date_now

        return crud.update_candle(db,candle)
    raise HTTPException(status_code=403,detail='deny: in user interface')
    

@app.post('/candle/remove/{candle_id}')
def remove_candle(candle_id:int,data:dict, db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    if ('rem_candle' not in data['components']):
        raise HTTPException(status_code=403,detail='deny: role access')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')

    date_now = datetime.datetime.now()
    history = schemas.HistoryBase(
        date_changes = date_now,
        fild_name='candles.life_time candles.is_burn candles.date_start candles.user_id',
        old_val=str(ca.life_time)+' '+str(ca.is_burn)+' '+str(ca.date_start)+' '+str(ca.user_id),
        new_val='0 0 '+str(date_now)+' -1',
        description='removing candle')
    histor = crud.create_history(db,history)

    ca.life_time = 0
    ca.is_burn = 0
    ca.user_id = -1
    ca.date_start = date_now
    res = crud.update_candle(db,ca)
    return res

@app.post('/candle/burn/{candle_id}')
def candle_burn(candle_id:int,data:dict,db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    if ('burn' not in data['components']):
        raise HTTPException(status_code=403,detail='deny: role access')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')

    if ca.is_burn == 1 :
        raise HTTPException(status_code=300, detail='candle already burn')

    date_now = datetime.datetime.now()
    history = schemas.HistoryBase(
        date_changes = date_now,
        fild_name='candles.is_burn candles.date_start',
        old_val=str(ca.is_burn)+' '+str(ca.date_start),
        new_val='1 '+str(date_now),
        description='burning candle id:'+str(ca.id))
    histor = crud.create_history(db,history)

    ca.is_burn = 1
    ca.date_start = date_now
    res = crud.update_candle(db,ca)
    return res

@app.post('/candle/unburn/{candle_id}')
def candle_unburn(candle_id:int,data:dict, db:Session = Depends(get_db)):
    """
    """
    #обработка ролевки
    
    if ('unburn' not in data['components']):
        raise HTTPException(status_code=403,detail='deny: role access')

    ca = crud.get_candle_by_id(db,candle_id)
    if ca is None:
        raise HTTPException(status_code=404, detail='candle not found')
    if ca.is_burn == 0:
        raise HTTPException(status_code=405, detail='candle already unburn')
    
    delta:datetime.timedelta = (datetime.datetime.now() - ca.date_start)
    new_life_time = ca.life_time - (delta.days*24*3600 + delta.seconds)
    date_now = datetime.datetime.now()
    history = schemas.HistoryBase(
        date_changes = date_now,
        fild_name='candles.is_burn candles.life_time',
        old_val=str(ca.is_burn)+' '+str(ca.life_time),
        new_val='0 '+str(new_life_time),
        description='burning candle id:'+str(ca.id))
    histor = crud.create_history(db,history)
        
    ca.is_burn = 0
    ca.life_time = new_life_time
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


@app.post('/chat/post_message')
def post_message(data:dict,db:Session = Depends(get_db)):
    user_db = crud.get_user(db,data['user_id'])
    if user_db is None:
        raise HTTPException(status_code=404, detail='user not found')
    