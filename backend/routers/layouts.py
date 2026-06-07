from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import (
    Layout,
    LayoutPocket,
    TierConfig,
    LayoutCreate,
    LayoutPocketUpdate,
    TierConfigUpdate,
    CompatibilityRequest,
    CompatibilityResult,
    Plant,
)
from data.seed_plants import COMPANIONS, INCOMPATIBLE
from datetime import datetime, timezone

router = APIRouter(prefix="/layouts", tags=["layouts"])

@router.get("/", response_model=list[Layout])
def get_layouts(session: Session = Depends(get_session)):
    return session.exec(select(Layout)).all()

@router.get("/{layout_id}")
def get_layout(layout_id: int, session: Session = Depends(get_session)):
    layout = session.get(Layout, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    
    pockets = session.exec(select(LayoutPocket).where(LayoutPocket.layout_id == layout_id)).all()

    tier_configs = session.exec(select(TierConfig).where(TierConfig.layout_id == layout_id)).all()

    return {
        "layout": layout,
        "pockets": pockets,
        "tier_configs": tier_configs
    }

@router.post("/", response_model=Layout)
def create_layout(data: LayoutCreate, session: Session = Depends(get_session)):
    layout = Layout(name=data.name, tiers=data.tiers, color=data.color)
    session.add(layout)
    session.commit()
    session.refresh(layout)

    # auto create tier configs so they default to original
    for tier_num in range(1, data.tiers + 1):
        tier_config = TierConfig(layout_id=layout.id, tier=tier_num)
        session.add(tier_config)

    session.commit()
    session.refresh(layout) # refresh after tier configs are saved
    return layout

@router.post("/check-compatibility", response_model=CompatibilityResult)
def check_compatibility(
    data: CompatibilityRequest,
    session: Session = Depends(get_session)
):
    """
    Check companion planting compatibility for a given list of plant IDs.
    """

    plants = [session.get(Plant, pid) for pid in data.plant_ids]
    plants = [p for p in plants if p] # filter out any None (invalid IDs)

    warnings = []
    suggestions = []

    for i, plant_a in enumerate(plants):
        for plant_b in plants[i + 1:]:
            a_incompatible = INCOMPATIBLE.get(plant_a.name, [])
            b_incompatible = INCOMPATIBLE.get(plant_b.name, [])

            if plant_b.name in a_incompatible or plant_a.name in b_incompatible:
                warnings.append(
                    f"⚠️ {plant_a.name} and {plant_b.name} will not get along!"
                )

            a_companions = COMPANIONS.get(plant_a.name, [])
            if plant_b.name in a_companions:
                suggestions.append(
                    f"{plant_a.name} and {plant_b.name} are a friendly match! They make great companions!"
                )
    
    return CompatibilityResult(
        compatible=len(warnings) == 0,
        warnings=warnings,
        suggestions=suggestions,
    )

@router.put("/{layout_id}/tiers")
def update_tier_config(
    layout_id: int,
    data: TierConfigUpdate, 
    session: Session = Depends(get_session)
):
    layout = session.get(Layout, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    
    existing = session.exec(
        select(TierConfig).where(
            TierConfig.layout_id == layout_id,
            TierConfig.tier == data.tier,
        )
    ).first()

    if existing:
        existing.tier_type = data.tier_type
        session.add(existing)
    else:
        session.add(TierConfig(
            layout_id=layout_id,
            tier=data.tier,
            tier_type=data.tier_type,
        ))

    session.commit()
    return {"message": f"Tier {data.tier} update to {data.tier_type}"}

@router.put("/{layout_id}/pockets")
def update_pocket(
    layout_id: int,
    data: LayoutPocketUpdate,
    session: Session = Depends(get_session)
):
    layout = session.get(Layout, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    
    # check that plant exists if one is provided
    if data.plant_id:
        plant = session.get(Plant, data.plant_id)
        if not plant:
            raise HTTPException(status=404, detail="Plant not found")
        
        # warn if plant doesn't support this tier type
        tier_config = session.exec(select(TierConfig).where(
            TierConfig.layout_id == layout_id,
            TierConfig.tier == data.tier,
        )).first()

        if tier_config and plant.tier_support.value == "original_only":
            if tier_config.tier_type.value == "leaf":
                raise HTTPException(
                    status_code=400,
                    detail=f"{plant.name} has deeper roots! Plant in an original tier pocket instead."
                )
    
    existing = session.exec(
        select(LayoutPocket).where(
            LayoutPocket.layout_id == layout_id,
            LayoutPocket.tier == data.tier,
            LayoutPocket.pocket == data.pocket
        )
    ).first()

    if existing:
        existing.plant_id = data.plant_id
        existing.quantity = data.quantity
        session.add(existing)
    else:
        session.add(LayoutPocket(
            layout_id=layout_id,
            tier=data.tier,
            pocket=data.pocket,
            plant_id=data.plant_id,
            quantity=data.quantity,
        ))

    layout.updated_at = datetime.now(timezone.utc)
    session.add(layout)
    session.commit()
    return {"message": "Pocket updated"}

@router.delete("/{layout_id}")
def delete_layout(layout_id: int, session: Session = Depends(get_session)):
    layout = session.get(Layout, layout_id)
    if not layout:
        raise HTTPException(status_code=404, detail="Layout not found")
    
    # delete child records first to avoid foreign key conflicts
    for model in [LayoutPocket, TierConfig]:
        rows = session.exec(
            select(model).where(model.layout_id == layout_id)
        ).all()
        for row in rows:
            session.delete(row)

    session.delete(layout)
    session.commit()
    return {"message": "Layout deleted"}
