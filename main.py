from fastapi import FastAPI
import models
from database import engine
from routers import address
from starlette.responses import RedirectResponse
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(address.router)
