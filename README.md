# Greenstalk Vertical Planter Planner

A helpful planner for Greenstalk planters with companion planting guidance. Built as a personal tool for planning across multiple towers (in Zone 10a currently).

## Demo instructions

1. Select or create a layout for your Greenstalk tower (3, 4, or 5-tier)
2. Assign plants to pockets from the plant library
3. Filter plants by type (veggie, herb, fruit, flower)
4. Check companion planting compatibility across your layout
5. Hover over a plant card for growing tips

## Tech stack

### Backend

- Python
- FastAPI
- SQLModel
- SQLite
  Also uncludes auto-generated interactive API docs via Swagger UI.

### Frontend

- Vanilla HTML
- CSS
- JavaScript (no build step)
  Could eventually be rebuilt/refactored to use React/Vite frameworks.

## Getting started

### Prereqs

- Python 3.11+

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

- API runs at: `http://localhost:8000`
- Interactive Swagger UI docs: `http://localhost:8000/docs`
- The database is created automatically on first run and seeded with 14 common plants.

### Frontend

```bash
cd frontend
python3 -m http.server 3000
```

- Open `http://localhost:3000` in your browser.

Note to self: the frontend must be served via a local server (not opened directly as a file) for fetch() requests to work. The backend must be running first.

## Data model

### Plant

| Field           | Type          | Notes                                     |
| --------------- | ------------- | ----------------------------------------- |
| id              | int           | Primary key                               |
| name            | str           | Plant name                                |
| type            | PlantType     | veggie, herb, fruit, flower               |
| sunlight        | SunlightLevel | full, partial, shade                      |
| water           | WaterLevel    | high, medium, low                         |
| tier_support    | TierSupport   | both, original_only                       |
| days_to_harvest | int           | Optional                                  |
| max_per_pocket  | int           | Optional — used for overcrowding warnings |
| notes           | str           | Growing tips                              |

### Layout

| Field            | Type            | Notes                          |
| ---------------- | --------------- | ------------------------------ |
| id               | int             | Primary key                    |
| name             | str             | User defined e.g. "Back Patio" |
| tiers            | int             | 3, 4, or 5                     |
| pockets_per_tier | int             | Always 6 for Greenstalk        |
| color            | GreenStalkColor | Optional                       |
| created_at       | datetime        | UTC                            |
| updated_at       | datetime        | UTC                            |

## a11y checklist

- [x] turn cards and pockets into buttons for better keyboard nav
- [x] add arial labels to cards and pockets
- [x] announce selected plant cards
- [ ] add appropriate roles to elements
- [ ] check and fix focus state on modal open
- [ ] allow ability to close modal with esc key
- [ ] announce compatibility results with aria-live region
- [ ] check and add focus outlines

## Icebox

### High priority

- [ ] Tier type toggle in the UI (`leaf` vs. `original` per tier with visual indicator)
- [ ] `max_per_pocket` warning — highlight overcrowded pockets with quantity input
- [ ] Expand plant library to full official Greenstalk list (~50 plants)
- [ ] ID-based compatibility lookups instead of name string matching (more robust)

### Medium priority

- [ ] LLM-powered compatibility advisor (swap in Claude API or local Ollama model to save on cost and for the ask of learning!)
- [ ] Seasonal rotation suggestions (i.e. flag plants that shouldn't follow each other in the same pocket)
- [ ] Sunlight zone mapping (i.e. warn if a shade plant is assigned to a top tier which has the most sun exposure)
- [ ] Plant search/filter by name in the sidebar
- [ ] Drag and drop pocket assignment (but think through a11y first)

### Low priority

- [ ] Alembic migrations for schema changes (i.e. replace manually deleting db and recreating workflow with light and safe way to make db migrations)
- [ ] Move to Postgres for production-grade constraint enforcement
- [ ] Mobile-friendly layout for use in the garden
- [ ] Export layout as PDF or image to reference while planting (just for the sake of learning!)
- [ ] Support multiple users / auth (currently single-user, no auth)
- [ ] Watering schedule based on water needs per tier
- [ ] Add ability to favorite layouts

## Fun but super optional nice to haves

- [ ] Drawings of all the possible plants
- [ ] Color match the containers
- [ ] Cute (but informative) error and warning messages
- [ ] Add germination times
- [ ] Add zones
- [ ] Maybe include the current weather in the corner?

## Known Limitations

- SQLite does not enforce enum constraints at the DB level — validation only happens at the API layer
- Compatibility engine keys on plant name (string matching) — renaming a plant would break compatibility lookups
- No authentication — the API is open, intended for local personal use only
- Frontend served via `python3 -m http.server` — not suitable for production deployment as-is
