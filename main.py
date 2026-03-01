from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Tambah visitor_id dalam model penerimaan data
class ClickData(BaseModel):
    page_url: str
    event_type: str
    referrer: Optional[str] = None
    visitor_id: str = "Tidak Diketahui" 

def init_db():
    conn = sqlite3.connect("saas_database.db")
    cursor = conn.cursor()
    
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
    
    # 2. Arahkan database cipta lajur baharu (visitor_id) jika ia belum ada
    try:
        cursor.execute('ALTER TABLE web_logs ADD COLUMN visitor_id TEXT')
    except:
        pass # Abaikan jika lajur ini sudah wujud
        
    conn.commit()
    conn.close()

init_db()

@app.post("/track")
async def track_event(data: ClickData, x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != "RAHSIA_123":
        raise HTTPException(status_code=403, detail="API Key tidak sah")

    masa_sekarang = datetime.now().isoformat()

    conn = sqlite3.connect("saas_database.db")
    cursor = conn.cursor()
    # 3. Masukkan visitor_id ke dalam simpanan database
    cursor.execute('''
        INSERT INTO web_logs (timestamp, api_key, page, event, referrer, visitor_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (masa_sekarang, x_api_key, data.page_url, data.event_type, data.referrer, data.visitor_id))
    
    conn.commit()
    conn.close()
    
    return {"status": "success"}

@app.get("/")
async def home():
    return {"message": "SaaS Admin Dashboard API sedang berjalan!"}

@app.get("/logs")
async def get_logs(x_admin_password: str = Header(None)):
    if not x_admin_password or x_admin_password != "ADMIN123":
        raise HTTPException(status_code=401, detail="Akses Ditolak. Kata laluan salah.")

    conn = sqlite3.connect("saas_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM web_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    senarai_log = []
    for row in rows:
        senarai_log.append({
            "id": row["id"],
            "timestamp": row["timestamp"],
            "api_key": row["api_key"],
            "page": row["page"],
            "event": row["event"],
            "referrer": row["referrer"],
            # 4. Hantar visitor_id ke Dashboard (Jika data lama, letak label "Data Lama")
            "visitor_id": row["visitor_id"] if "visitor_id" in row.keys() else "Data Lama"
        })
        
    return senarai_log
