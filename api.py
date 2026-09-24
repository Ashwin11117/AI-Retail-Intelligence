from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI(title="RetailOS Edge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('retailos.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def read_root():
    return {"message": "RetailOS Edge Gateway is ONLINE."}

@app.get("/api/shopper-status")
def get_shopper_status():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Shopper_Logs ORDER BY timestamp DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "edge_status": "ONLINE (LOCAL)",
                "timestamp": row['timestamp'], 
                "active_shoppers": row['active_shoppers'],
                "fps": 24.5,
                "cpu_load": "18%",
                "shelf_stock_level": "84%",       # New inventory metric
                "restock_alerts": 1              # Simulated active restock notice
            }
        else:
            return {
                "edge_status": "WAITING FOR AI", 
                "active_shoppers": 0, 
                "fps": 0, 
                "cpu_load": "0%",
                "shelf_stock_level": "0%",
                "restock_alerts": 0
            }
            
    except sqlite3.OperationalError:
        return {"error": "Database not found. Run the AI engine first!"}