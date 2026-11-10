# How We Built the Editable Sections Feature
## A learning guide — written for you to read at your own pace

---

## The Goal

Before this feature, section names like "Salads & Bowls" and "Fish & Seafood" were
hardcoded in the HTML files. Only a developer could change them by editing code.

After this feature, the client can log into the admin panel, go to the Sections tab,
type a new name, click Save — and the website updates instantly. No developer needed.

---

## The 4 Layers We Built

```
Layer 1 — Database      backend/app/database.py
Layer 2 — Models        backend/app/models.py
Layer 3 — API Routes    backend/app/routes/sections.py  (new file)
Layer 4 — Frontend      public/admin.html + public/index.html
```

Think of it like a restaurant kitchen:
- Database = the fridge (stores the data)
- Models = the health inspector (enforces rules on what goes in/out)
- API Routes = the waiter (carries data between kitchen and customer)
- Frontend = the dining room (what the customer actually sees)

---

## Layer 1 — database.py

### What is this file?
Every table that exists in PostgreSQL is defined here. When the app starts,
it runs all these definitions to make sure the tables exist.

### What we added

**1. The table definition:**
```python
CREATE_SECTIONS = """
CREATE TABLE IF NOT EXISTS sections (
    key        TEXT PRIMARY KEY,
    label      TEXT NOT NULL,
    icon       TEXT NOT NULL DEFAULT 'fa-utensils',
    ornament   BOOLEAN NOT NULL DEFAULT false,
    sort_order INTEGER NOT NULL DEFAULT 999
)
"""
```

Breaking it down:
- `CREATE TABLE IF NOT EXISTS` = create this table, but skip if it already exists
- `key TEXT PRIMARY KEY` = internal ID like 'salads'. Must be unique. Never changes.
- `label TEXT NOT NULL` = display name like 'Salads & Bowls'. Cannot be empty.
- `icon TEXT NOT NULL DEFAULT 'fa-utensils'` = Font Awesome icon. Has a fallback.
- `ornament BOOLEAN` = true/false. Controls a decorative divider on the website.
- `sort_order INTEGER` = controls display order. 1 = first, 20 = last.

**2. The default data:**
```python
DEFAULT_SECTIONS = [
    ("starters", "Starters", "fa-leaf", True, 1),
    ("salads", "Salads & Bowls", "fa-seedling", False, 2),
    # ... all 20 sections
]
```

This is a Python list. Each item is a tuple (a group of values in round brackets).
Each tuple = one row = one section. The 5 values match the 5 columns in the table.

**3. Telling init_db to run it:**
```python
await conn.execute(CREATE_SECTIONS)
for key, label, icon, ornament, sort_order in DEFAULT_SECTIONS:
    await conn.execute(
        "INSERT INTO sections ... ON CONFLICT (key) DO NOTHING",
        key, label, icon, ornament, sort_order,
    )
```

- `await` = wait for this to finish before moving on
- `conn.execute()` = send this SQL to the database and run it
- `for ... in DEFAULT_SECTIONS:` = loop through every section in the list
- `ON CONFLICT (key) DO NOTHING` = if a section already exists, skip it silently

---

## Layer 2 — models.py

### What is this file?
Defines the rules for what data is allowed in and out of the API.
Uses a library called Pydantic which automatically validates data.

### What we added

**Model 1 — Section (data going OUT to the browser):**
```python
class Section(BaseModel):
    key: str
    label: str
    icon: str
    ornament: bool
    sort_order: int
```

This says: when the API sends a section to the browser, it must have all 5 fields
with the correct types. `str` = text. `bool` = true/false. `int` = whole number.

**Model 2 — SectionLabelUpdate (data coming IN from admin):**
```python
class SectionLabelUpdate(BaseModel):
    label: str = Field(..., min_length=1, max_length=80)
```

This says: when admin renames a section, they can ONLY send a label.
- `...` = this field is required, cannot be left out
- `min_length=1` = cannot be empty
- `max_length=80` = cannot be more than 80 characters

The admin cannot change the key or sort_order through this. Pydantic rejects anything
else automatically. This is a security feature.

---

## Layer 3 — routes/sections.py (new file)

### What is this file?
Defines the two API addresses (routes) that the browser can call.

### The imports at the top
```python
from fastapi import APIRouter, Depends, HTTPException
from app.auth import require_admin
from app.database import get_db
from app.models import Section, SectionLabelUpdate

router = APIRouter(prefix="/api")
```

- `APIRouter` = a container for our routes
- `Depends` = tells FastAPI to run a function first (like getting a DB connection)
- `HTTPException` = lets us send error responses like 404
- `require_admin` = already-written function that checks for a valid admin token
- `get_db` = gives us a live database connection for each request
- `prefix="/api"` = all routes in this file start with /api automatically

### Route 1 — GET /api/sections (anyone can read)
```python
@router.get("/sections", response_model=list[Section])
async def get_sections(
    db: asyncpg.Connection = Depends(get_db),
) -> list[Section]:
    rows = await db.fetch(
        "SELECT key, label, icon, ornament, sort_order FROM sections ORDER BY sort_order"
    )
    return [Section(**dict(row)) for row in rows]
```

- `@router.get` = this responds to GET requests (reading data)
- `"/sections"` = the URL address (becomes /api/sections with the prefix)
- `response_model=list[Section]` = format the response as a list of Section objects
- `db.fetch(...)` = run this SQL and return ALL matching rows
- `ORDER BY sort_order` = return sections in display order (1, 2, 3...)
- `[Section(**dict(row)) for row in rows]` = convert each DB row into a Section object

### Route 2 — PATCH /api/admin/sections/{key} (admin only)
```python
@router.patch("/admin/sections/{key}", dependencies=[Depends(require_admin)])
async def update_section_label(
    key: str,
    payload: SectionLabelUpdate,
    db: asyncpg.Connection = Depends(get_db),
) -> Section:
    row = await db.fetchrow(
        "UPDATE sections SET label = $1 WHERE key = $2 "
        "RETURNING key, label, icon, ornament, sort_order",
        payload.label.strip(), key,
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return Section(**dict(row))
```

- `@router.patch` = PATCH means "update part of something" (just the label)
- `{key}` in the URL = a variable. Calling /api/admin/sections/salads sets key='salads'
- `dependencies=[Depends(require_admin)]` = reject the request if not logged in as admin
- `payload: SectionLabelUpdate` = the body of the request, validated by Pydantic
- `db.fetchrow(...)` = run SQL and return ONE row (not a list)
- `UPDATE sections SET label = $1 WHERE key = $2` = change the label for this key
- `$1, $2` = placeholders replaced by actual values. Safer than putting values in the SQL directly.
- `RETURNING ...` = after updating, return the updated row immediately
- `if row is None: raise HTTPException(404)` = if the key doesn't exist, return a 404 error

### Why PATCH and not PUT?
- PUT = replace the whole thing
- PATCH = update just one part
We only change the label, so PATCH is the correct choice.

---

## Layer 4 — main.py

Two lines added to register the new router:

```python
from app.routes.sections import router as sections_router
app.include_router(sections_router)
```

FastAPI does not know a router exists until you import it and include it here.
This is like adding a new department to a company — you have to register it officially.

---

## Layer 5 — admin.html

### What changed
The hardcoded `SECTION_LABELS` object was replaced with a dynamic fetch:

```javascript
// BEFORE (hardcoded — only a developer can change this):
const SECTION_LABELS = {
  salads: 'Salads',
  fish: 'Fish & Seafood',
  // ...
};

// AFTER (dynamic — reads from database):
let SECTION_LABELS = {};

async function loadSections() {
  const res = await fetch(`${API}/api/sections`);
  sectionsData = await res.json();
  SECTION_LABELS = {};
  sectionsData.forEach(s => { SECTION_LABELS[s.key] = s.label; });
}
```

### The Sections Tab
A new tab was added to the admin panel. When clicked, it:
1. Calls `loadSectionsTab()` which fetches all sections from the API
2. Renders each section as a row with an input field and Save button
3. When Save is clicked, `saveSectionLabel(key)` sends a PATCH request to the API
4. The API updates the database and returns the updated section
5. The label updates instantly on screen

```javascript
async function saveSectionLabel(key) {
  const input = document.getElementById(`sec-input-${key}`);
  const label = input.value.trim();
  const res = await fetch(`${API}/api/admin/sections/${key}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
    body: JSON.stringify({ label }),
  });
  const updated = await res.json();
  SECTION_LABELS[key] = updated.label;
}
```

---

## Layer 6 — index.html

The hardcoded `SECTION_META` object was replaced with a dynamic fetch:

```javascript
// BEFORE:
const SECTION_META = {
  salads: { label: 'Salads', icon: 'fa-seedling', ornament: false },
  // ...
};

// AFTER:
let SECTION_META = {};

async function loadSectionMeta() {
  const res = await fetch(`${API_BASE}/api/sections`);
  const sections = await res.json();
  SECTION_META = {};
  sections.forEach(s => {
    SECTION_META[s.key] = { label: s.label, icon: s.icon, ornament: s.ornament };
  });
}
```

Then `loadSectionMeta()` runs before `loadMenu()` so section names are ready
before the menu tries to display them.

---

## The Critical Rule — Key vs Label

| Thing | Example | Who sees it | Can it change? |
|-------|---------|-------------|----------------|
| Key   | `salads` | Database, code only | NEVER |
| Label | `Salads & Bowls` | Users on the website | Anytime via admin |

The key is the internal ID. Every menu item in the database has a `section` column
that stores the key. If you changed the key from `salads` to something else, every
salad item would become orphaned — the app could not find which section they belong to.

The label is just a display name. Changing it only affects what humans read.
The database connection between items and sections is never broken.

---

## Files Changed Summary

| File | What changed |
|------|-------------|
| `backend/app/database.py` | Added sections table + 20 default rows + init_db wiring |
| `backend/app/models.py` | Added Section and SectionLabelUpdate classes |
| `backend/app/routes/sections.py` | NEW FILE — 2 API endpoints |
| `backend/app/main.py` | Registered the new sections router |
| `public/admin.html` | Dynamic sections + Sections tab UI |
| `public/index.html` | Dynamic section names from API |
