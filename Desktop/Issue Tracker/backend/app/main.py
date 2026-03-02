from fastapi import FastAPI
from .database import engine, Base
from . import models
from .routes import projects
from .routes import users
from .routes import issues

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(projects.router)
app.include_router(users.router)
app.include_router(issues.router)


@app.get("/")
def read_root():
    return {"message": "Issue Tracker API running"}