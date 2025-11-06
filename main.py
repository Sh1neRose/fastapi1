from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, String, select
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, sessionmaker
from typing import Annotated
from pydantic import BaseModel, Field

app = FastAPI()

engine = create_engine("postgresql+psycopg2://pp04user:pp04password@localhost:5432/pp04DB", echo=True)

class Base(DeclarativeBase):
    pass

def create_db_and_tables():
    Base.metadata.create_all(engine)

new_session = sessionmaker(engine, expire_on_commit=False)

def get_session():
    with new_session() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

class UserAddSchema(BaseModel):
    name: str = Field(max_length=30)

class UserSchema(UserAddSchema):
    id: int

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/books")
def add_user(data: UserAddSchema, session: SessionDep):
    user = User(
        name=data.name
    )
    session.add(user)
    session.commit()
    return {"status": True}

@app.get("/books")
def get_users(session: SessionDep):
    query = select(User)
    result = session.execute(query)
    return result.scalars().all()

@app.get("/books/{user_id}/")
def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/books/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"status": True}