import os
from pathlib import Path
from typing import List

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db
from .llm.base import LLMProvider
from .llm.factory import get_llm_provider
from .rag.ingest import ingest_documents_from_directory
from .rag.rag import get_collection
from .services.question_service import build_contextual_prompt

DEFAULT_DOCUMENTS_DIR = Path(__file__).resolve().parent / "rag" / "documents"

# Create tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="JL-rag API")


def reset_and_ingest_documents(directory: str | None = None) -> int:
    collection = get_collection(reset=True)
    documents_dir = directory or os.getenv(
        "DOCUMENTS_DIR",
        str(DEFAULT_DOCUMENTS_DIR),
    )
    return ingest_documents_from_directory(documents_dir, collection=collection)


@app.on_event("startup")
def startup_event() -> None:
    count = reset_and_ingest_documents()
    print(f"Ingested {count} document chunks on startup")


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
    #db_user = db.query(models.User).filter(models.User.id == u_id).first()
   # if not db_user:
    #    raise HTTPException(status_code=404, detail="User not found")

    prompt = build_contextual_prompt(payload.questions)
    answer_text = llm.answer(prompt)

    db_message = models.Message(
        u_id=u_id,
        questions=payload.questions,
        answer=answer_text,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
 

@app.post("/ingest")
def ingest_documents(directory: str):
    count = reset_and_ingest_documents(directory)
    return {"count": count, "directory": directory}


@app.get("/")
def root():
    return {"message": "Users & Messages API is running"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        reload=False,
    )

