from api import auth, user
from db.database import Base, engine
from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(user.router)
