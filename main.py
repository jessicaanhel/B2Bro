from fastapi import FastAPI, HTTPException, Query
from db import CarSpeakerDB
from constants import DB_PATH

app = FastAPI()
db = CarSpeakerDB(DB_PATH)

@app.get("/models/")
def get_models(make: str = Query(..., description="Car make, e.g. 'audi'")):
    models = db.get_models_by_make(make)
    if not models:
        raise HTTPException(status_code=404, detail=f"No models found for make '{make}'")
    return {"make": make.lower(), "models": models}

@app.get("/speaker-size/")
def get_speaker_size(make: str, model: str, year: int):
    make_model_year = f"{make} {model} {year}"
    car = db.find_car(make_model_year)

    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    car_id = car["id"]
    front_door = db.get_door_size(car_id, 'front')
    rear_door = db.get_door_size(car_id, 'rear')

    return {
        "make": car["make"],
        "model": car["model"],
        "size_front_cm": front_door,
        "size_rear_cm": rear_door,
    }

if __name__ == "__main__":
    db.debug_print_all()
    data = []
    db.add_no_duplicates(data)
