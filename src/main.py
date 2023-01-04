from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

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