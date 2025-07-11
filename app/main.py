from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from .db import Base, engine
from .routers import auth, products, orders

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Freshcart Express")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)

os.makedirs("media", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")
