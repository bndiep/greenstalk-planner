from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from enums import PlantType, SunlightLevel, WaterLevel, TierType, TierSupport, GreenStalkColor

# DB tables
class Plant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: PlantType
    sunlight: SunlightLevel
    water: WaterLevel
    days_to_harvest: Optional[int] = None
    max_per_pocket: Optional[int] = None # None just means there is no limit defined
    tier_support: TierSupport = TierSupport.both
    notes: Optional[str] = None
    # TODO: could also include best season to grow in? may need to think about adding zones too!
    # TODO: could also include seed germination info as well

class Layout(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tiers: int = 5
    pockets_per_tier: int = 6
    color: Optional[GreenStalkColor] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class TierConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    layout_id: int = Field(foreign_key="layout.id")
    tier: int
    tier_type: TierType = TierType.original 

class LayoutPocket(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    layout_id: int = Field(foreign_key="layout.id")
    tier: int
    pocket: int
    plant_id: Optional[int] = Field(default=None, foreign_key="plant.id")
    quantity: int = 1 # num of seeds/seedlings in this pocket

# request/response schemas
class LayoutCreate(SQLModel):
    name: str
    tiers: int = 5
    color: Optional[GreenStalkColor] = None

class TierConfigUpdate(SQLModel):
    tier: int
    tier_type: TierType

class LayoutPocketUpdate(SQLModel):
    tier: int
    pocket: int
    plant_id: Optional[int] = None
    quantity: int = 1

class CompatibilityRequest(SQLModel):
    plant_ids: list[int]

class CompatibilityResult(SQLModel):
    compatible: bool
    warnings: list[str]
    suggestions: list[str]
