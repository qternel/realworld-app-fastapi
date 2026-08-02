from api import articles, auth, profiles, user
from db.database import Base, engine
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

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
