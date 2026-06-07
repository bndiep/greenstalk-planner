from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Plant

router = APIRouter(prefix="/plants", tags=["plants"])

@router.get("/", response_model=list[Plant])
def get_plants(session: Session = Depends(get_session)):
    return session.exec(select(Plant)).all()

@router.get("/{plant_id}", response_model=Plant)
def get_plant(plant_id: int, session: Session = Depends(get_session)):
    plant = session.get(Plant, plant_id)
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    return plant
