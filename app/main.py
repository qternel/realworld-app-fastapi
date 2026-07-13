from api import auth, profiles, user
from db.database import Base, engine
from fastapi import FastAPI

app = FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profiles.router)
