import json, re
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from PIL import UnidentifiedImageError
from model_handler import handler

app = FastAPI(title="KidVocab Vision API")

FRUIT_DATA    = json.loads(Path("fruit_data.json").read_text(encoding="utf-8"))
IMAGENET_DATA = json.loads(Path("imagenet_vn.json").read_text(encoding="utf-8"))
ALL_OBJECTS   = {**IMAGENET_DATA, **FRUIT_DATA}

def _fallback_info(label: str) -> dict:
    name = re.sub(r"[_-]", " ", label).title()
    return {
        "nameEn": name, "nameVn": name,
        "emoji": "📦", "phonetic": "",
        "color": "#78909C", "category": "object",
        "funFact": f"This is a {name}!",
    }

@app.on_event("startup")
async def startup():
    try:
        handler.load()
    except Exception as e:
        print(f"Startup error: {e}")

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "fruit_ready":    handler.fruit_ready,
        "imagenet_ready": handler.imagenet_ready,
        "total_objects":  len(ALL_OBJECTS),
    }

@app.get("/api/all-objects")
def get_all():
    return ALL_OBJECTS

@app.get("/api/object/{label:path}")
def get_object(label: str):
    return ALL_OBJECTS.get(label) or _fallback_info(label)

@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    if not contents:
        raise HTTPException(400, "Empty file")

    if not handler.imagenet_ready:
        import random
        label = random.choice(list(ALL_OBJECTS.keys()))
        return {"source": "demo", "demo_mode": True,
                "results": [{"label": label, "confidence": round(random.uniform(.7, .99), 3)}]}

    try:
        result = handler.predict(contents)
    except UnidentifiedImageError:
        raise HTTPException(400, "Uploaded file is not a valid image")
    except OSError:
        raise HTTPException(400, "Cannot read uploaded image")
    result["demo_mode"] = False
    return result

app.mount("/", StaticFiles(directory="static", html=True), name="static")
