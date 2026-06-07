from sqlmodel import Session, select
from models import Plant
from enums import PlantType, SunlightLevel, WaterLevel, TierSupport

PLANTS = [
    {
        "name": "Tomato",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.high,
        "days_to_harvest": 75,
        "max_per_pocket": 1,
        "tier_support": TierSupport.original_only,
        "notes": "Needs a plant support or trellis.",
    },
    {
        "name": "Basil",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.medium,
        "days_to_harvest": 30,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Pinch flowers to keep producing.",
    },
    {
        "name": "Lettuce",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.partial,
        "water": WaterLevel.medium,
        "days_to_harvest": 45,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Bolts in the heat.",
    },
    {
        "name": "Spinach",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.partial,
        "water": WaterLevel.medium,
        "days_to_harvest": 40,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Bolts in the heat.",
    },
    {
        "name": "Kale",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.medium,
        "days_to_harvest": 60,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Very cold hardy.",
    },
    {
        "name": "Mint",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.partial,
        "water": WaterLevel.medium,
        "days_to_harvest": 30,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Beware. Easily spreads and takes over EVERYTHING!",
    },
    {
        "name": "Strawberry",
        "type": PlantType.fruit,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.medium,
        "days_to_harvest": 90,
        "max_per_pocket": 1,
        "tier_support": TierSupport.both,
        "notes": "When starting from bareroots, clip flowers to allow leaves to full establish.",
    },
    {
        "name": "Pepper",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.medium,
        "days_to_harvest": 80,
        "max_per_pocket": 1,
        "tier_support": TierSupport.original_only,
        "notes": "Loves heat.",
    },
    {
        "name": "Rosemary",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.low,
        "days_to_harvest": 90,
        "max_per_pocket": 1,
        "tier_support": TierSupport.both,
        "notes": "Drought tolerant once established.",
    },
    {
        "name": "Thyme",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.low,
        "days_to_harvest": 60,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Great companion for most veggies.",
    },
    {
        "name": "Chives",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.medium,
        "days_to_harvest": 30,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Plant in clusters. Deters aphids.",
    },
    {
        "name": "Arugula",
        "type": PlantType.veggie,
        "sunlight": SunlightLevel.partial,
        "water": WaterLevel.medium,
        "days_to_harvest": 35,
        "max_per_pocket": 3,
        "tier_support": TierSupport.both,
        "notes": "Peppery flavor. Bolts quickly in the heat.",
    },
    {
        "name": "Parsley",
        "type": PlantType.herb,
        "sunlight": SunlightLevel.partial,
        "water": WaterLevel.medium,
        "days_to_harvest": 70,
        "max_per_pocket": 2,
        "tier_support": TierSupport.both,
        "notes": "Slow to germinate. For patient gardeners only.",
    },
    {
        "name": "Marigold",
        "type": PlantType.flower,
        "sunlight": SunlightLevel.full,
        "water": WaterLevel.low,
        "days_to_harvest": None,
        "max_per_pocket": 1,
        "tier_support": TierSupport.both,
        "notes": "Natural (and pretty) pest deterrent. Great companion plant.",
    },
]

# companion planting data
# TODO: plain dict for now but can be swapped for LLM call later in next iteration
COMPANIONS: dict[str, list[str]] = {
    "Tomato": ["Basil", "Marigold", "Chives", "Parsely"],
    "Basil": ["Tomato", "Pepper"],
    "Lettuce": ["Chives", "Strawberry", "Thyme"],
    "Spinach": ["Strawverry", "Lettuce"],
    "Kale": ["Thyme", "Rosemary"],
    "Mint": [],
    "Strawberry": ["Thyme", "Spinach", "Lettuce"],
    "Pepper": ["Basil", "Marigold"],
    "Cucumber": ["Marigold", "Chives"],
    "Rosemary": ["Kale", "Thyme"],
    "Thyme": ["Rosemary", "Kale", "Strawberry", "Lettuce", "Tomato"],
    "Chives": ["Tomato", "Chives", "Lettuce"],
    "Arugula": ["Lettuce", "Spinach"],
    "Parsley": ["Tomato", "Chives"],
    "Marigold": ["Tomato", "Pepper"],
}

INCOMPATIBLE: dict[str, list[str]] = {
    "Mint": ["Basil", "Rosemary"],
    "Tomato": ["Mint"],
    "Rosemary": ["Mint"],
    "Basil": ["Mint"],
    "Arugula": ["Mint"]
}

def seed(session: Session):
    existing = session.exec(select(Plant)).all()
    if existing:
        return # already seeded so avoid duplicating
    
    for p in PLANTS:
        session.add(Plant(**p))
    
    session.commit()
    print(f"✅ Seeded {len(PLANTS)} plants")
    