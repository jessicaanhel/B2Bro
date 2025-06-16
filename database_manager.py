import sqlite3
from fastapi import FastAPI, HTTPException, Query

app = FastAPI()
DB_PATH = 'speaker_sizes.db'


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speaker_sizes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT,
            model TEXT,
            year_start INTEGER,
            year_end INTEGER,
            size_front_cm REAL,
            size_rear_cm REAL
        )
    ''')
    conn.commit()
    conn.close()

def clean_and_add_to_db(cars, clear_first=True):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if clear_first:
        cursor.execute('DELETE FROM speaker_sizes')
        print("Cleared the speaker_sizes table before inserting new data.")

    cars_lower = [(make.lower(), model.lower(), ys, ye, sf, sr) for (make, model, ys, ye, sf, sr) in cars]

    cursor.executemany('''
        INSERT INTO speaker_sizes (make, model, year_start, year_end, size_front_cm, size_rear_cm)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', cars_lower)
    conn.commit()
    print(f"Added {cursor.rowcount} rows to the database.")
    conn.close()


def add_to_db_no_duplicates(cars):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for car in cars:
        make, model, ys, ye, sf, sr = car
        make, model = make.lower(), model.lower()
        cursor.execute('''
            SELECT id FROM speaker_sizes WHERE make = ? AND model = ? AND year_start = ? AND year_end = ?
        ''', (make, model, ys, ye))
        exists = cursor.fetchone()
        if not exists:
            cursor.execute('''
                INSERT INTO speaker_sizes (make, model, year_start, year_end, size_front_cm, size_rear_cm)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (make, model, ys, ye, sf, sr))
            print(f"Inserted {make} {model} {ys}-{ye}")
        else:
            print(f"Skipped duplicate {make} {model} {ys}-{ye}")

    conn.commit()
    conn.close()

def check_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM speaker_sizes")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    conn.close()

@app.get("/models/")
def get_models_by_make(make: str = Query(..., description="Car make, e.g. 'audi'")):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT DISTINCT model FROM speaker_sizes
        WHERE make = ?
        ORDER BY model
    '''
    cursor.execute(query, (make.lower(),))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No models found for make '{make}'")

    models = [row["model"] for row in rows]
    return {"make": make.lower(), "models": models}


@app.get("/speaker-size/")
def get_speaker_size(make: str, model: str, year: int):
    conn = get_db_connection()
    query = '''
        SELECT * FROM speaker_sizes
        WHERE make = ? AND model = ? AND year_start <= ? AND year_end >= ?
        LIMIT 1
    '''
    row = conn.execute(query, (make.lower(), model.lower(), year, year)).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Data not found")
    return {
        "make": row["make"],
        "model": row["model"],
        "year_start": row["year_start"],
        "year_end": row["year_end"],
        "size_front_cm": row["size_front_cm"],
        "size_rear_cm": row["size_rear_cm"],
    }

if __name__ == "__main__":
    check_db()

    data = [

    ]
    # add_to_db_no_duplicates(data)

