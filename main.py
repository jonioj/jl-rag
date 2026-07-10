from typing import List
import llm
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, get_db
from llm.base import LLMProvider
from llm.factory import get_llm_provider
 
# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Users & Messages API")


# ---------------- Users ----------------

@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=List[schemas.UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.User).offset(skip).limit(limit).all()


@app.get("/users/{user_id}", response_model=schemas.UserWithMessages)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}


# ---------------- Messages ----------------

@app.post("/messages", response_model=schemas.MessageOut)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == message.u_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_message = models.Message(
        u_id=message.u_id,
        questions=message.questions,
        answer=message.answer,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@app.get("/messages", response_model=List[schemas.MessageOut])
def list_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Message).offset(skip).limit(limit).all()


@app.get("/messages/{message_id}", response_model=schemas.MessageOut)
def get_message(message_id: int, db: Session = Depends(get_db)):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message


@app.get("/users/{user_id}/messages", response_model=List[schemas.MessageOut])
def get_messages_for_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db.query(models.Message).filter(models.Message.u_id == user_id).all()


@app.delete("/messages/{message_id}")
def delete_message(message_id: int, db: Session = Depends(get_db)):
    db_message = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not db_message:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(db_message)
    db.commit()
    return {"detail": "Message deleted"}


@app.post("/users/{u_id}/ask", response_model=schemas.MessageOut)
def ask_question(
    u_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    llm: LLMProvider = Depends(get_llm_provider),
):
    db_user = db.query(models.User).filter(models.User.id == u_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
 
    answer_text = llm.answer(payload.questions)
 
    db_message = models.Message(
        u_id=u_id,
        questions=payload.questions,
        answer=answer_text,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
 

@app.get("/")
def root():
    return {"message": "Users & Messages API is running"}

