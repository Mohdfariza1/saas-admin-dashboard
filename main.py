from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import sqlite3  # Kita bawa masuk fungsi database SQLite

app = FastAPI()

# Benarkan Dashboard (Frontend) akses API kita
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClickData(BaseModel):
    page_url: str
    event_type: str
    referrer: Optional[str] = None

# --- BAHAGIAN SETUP DATABASE SQLITE ---
def init_db():
    # Ini akan mencipta fail 'saas_database.db' secara automatik
    conn = sqlite3.connect("saas_database.db")
    cursor = conn.cursor()
    
    # Buat jadual (table) jika ia belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS web_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            api_key TEXT,
            page TEXT,
            event TEXT,
            referrer TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Jalankan fungsi setup database sebaik sahaja server dihidupkan
init_db()
# ------------------------------------

@app.post("/track")
async def track_event(data: ClickData, x_api_key: str = Header(None)):
    # Semak API Key
    if not x_api_key or x_api_key != "RAHSIA_123":
        raise HTTPException(status_code=403, detail="API Key tidak sah")

    masa_sekarang = datetime.now().isoformat()

    # Simpan data yang masuk ke dalam database
    conn = sqlite3.connect("saas_database.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO web_logs (timestamp, api_key, page, event, referrer)
        VALUES (?, ?, ?, ?, ?)
    ''', (masa_sekarang, x_api_key, data.page_url, data.event_type, data.referrer))
    
    conn.commit()
    conn.close()
    
    return {"status": "success", "message": "Data berjaya direkodkan ke Database SQLite!"}

@app.get("/")
async def home():
    return {"message": "SaaS Admin Dashboard API sedang berjalan dengan Database SQLite!"}

@app.get("/logs")
async def get_logs():
    # Baca semua data dari database untuk dihantar ke Dashboard
    conn = sqlite3.connect("saas_database.db")
    conn.row_factory = sqlite3.Row # Supaya data mudah ditukar jadi JSON format
    cursor = conn.cursor()
    
    # Ambil data susun dari yang paling baru
    cursor.execute("SELECT * FROM web_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    # Tukar format data supaya Dashboard HTML kita faham
    senarai_log = []
    for row in rows:
        senarai_log.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "api_key": row["api_key"],
            "page": row["page"],
            "event": row["event"],
            "referrer": row["referrer"]
        })
        
    return senarai_log