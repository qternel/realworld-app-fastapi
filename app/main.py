from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api import articles, auth, profiles, user
from app.db.database import Base, engine

app = FastAPI()


@app.exception_handler(HTTPException)
async def custom_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"errors": {"body": [exc.detail]}}
    )


Base.metadata.create_all(engine)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profiles.router)
app.include_router(articles.router)
