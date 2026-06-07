from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables, engine
from contextlib import asynccontextmanager
from sqlmodel import Session
from data.seed_plants import seed
from routers import plants, layouts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    create_db_and_tables()
    with Session(engine) as session:
        seed(session)
    yield
    # shutdown tbd

app = FastAPI(
    title="Greenstalk Planner API",
    description="Plan your Greenstalk vertical garden.",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(plants.router)
app.include_router(layouts.router)

@app.get("/")
def root():
    return {"message": "Greenstalk Planner API is running"}

@app.get("/health")
def health(): 
    return {"status": "ok"}
