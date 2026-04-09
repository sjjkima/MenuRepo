from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import sqlite3
import json
import qrcode
import io
import os
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List

app = FastAPI(title="Restaurant Ordering System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/orders.db")
QR_DIR = os.path.join(os.path.dirname(__file__), "../qr_codes")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# ─── Database Setup ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_number INTEGER NOT NULL,
            items TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ─── Models ────────────────────────────────────────────────────────────────────
class OrderItem(BaseModel):
    name: str
    qty: int
    price: float = 0.0

class OrderRequest(BaseModel):
    table: int
    items: List[OrderItem]
    total: float

# ─── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Restaurant Ordering API", "status": "running"}


@app.post("/order")
def create_order(order: OrderRequest):
    conn = get_db()
    items_json = json.dumps([i.dict() for i in order.items])
    cursor = conn.execute(
        "INSERT INTO orders (table_number, items, total_price) VALUES (?, ?, ?)",
        (order.table, items_json, order.total)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return {"success": True, "order_id": order_id, "message": "Order received!"}


@app.get("/orders")
def get_orders():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    orders = []
    for row in rows:
        orders.append({
            "id": row["id"],
            "table_number": row["table_number"],
            "items": json.loads(row["items"]),
            "total_price": row["total_price"],
            "status": row["status"],
            "created_at": row["created_at"]
        })
    return orders


@app.get("/orders/{table_number}")
def get_table_order(table_number: int):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM orders WHERE table_number = ? AND status != 'cleared' ORDER BY created_at DESC LIMIT 1",
        (table_number,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row["id"],
        "table_number": row["table_number"],
        "items": json.loads(row["items"]),
        "total_price": row["total_price"],
        "status": row["status"],
        "created_at": row["created_at"]
    }


@app.get("/orders/{table_number}/all")
def get_all_table_orders(table_number: int):
    """Get all active (non-cleared) orders for a table, newest first."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE table_number = ? AND status != 'cleared' ORDER BY created_at DESC",
        (table_number,)
    ).fetchall()
    conn.close()
    return [{
        "id": row["id"],
        "table_number": row["table_number"],
        "items": json.loads(row["items"]),
        "total_price": row["total_price"],
        "status": row["status"],
        "created_at": row["created_at"]
    } for row in rows]


@app.patch("/order/{table_number}/status")
def update_status(table_number: int, status: str):
    conn = get_db()
    conn.execute(
        "UPDATE orders SET status = ? WHERE table_number = ? AND status != 'cleared'",
        (status, table_number)
    )
    conn.commit()
    conn.close()
    return {"success": True}


@app.delete("/order/by-id/{order_id}")
def clear_order_by_id(order_id: int):
    """Clear a specific order by ID. Defined BEFORE the wildcard route to avoid conflicts."""
    conn = get_db()
    conn.execute("UPDATE orders SET status = 'cleared' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Order {order_id} cleared"}


@app.delete("/order/{table_number}")
def clear_table(table_number: int):
    conn = get_db()
    conn.execute(
        "UPDATE orders SET status = 'cleared' WHERE table_number = ? AND status != 'cleared'",
        (table_number,)
    )
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Table {table_number} cleared"}


@app.get("/generate_qr/{table_number}")
def generate_qr(table_number: int, base_url: str = "http://localhost:8080"):
    url = f"{base_url}/customer.html?table={table_number}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to disk
    file_path = os.path.join(QR_DIR, f"table_{table_number}.png")
    img.save(file_path)

    # Stream as response
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=table_{table_number}_qr.png"}
    )


@app.get("/analytics")
def get_analytics():
    conn = get_db()
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    all_rows = conn.execute(
        "SELECT * FROM orders WHERE status != 'cleared'"
    ).fetchall()
    conn.close()

    orders = [{
        "id": r["id"],
        "table_number": r["table_number"],
        "items": json.loads(r["items"]),
        "total_price": r["total_price"],
        "created_at": r["created_at"]
    } for r in all_rows]

    def parse_dt(s):
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        except:
            return datetime.utcnow()

    def revenue(orders_list):
        return round(sum(o["total_price"] for o in orders_list), 2)

    today_orders = [o for o in orders if parse_dt(o["created_at"]) >= today_start]
    week_orders  = [o for o in orders if parse_dt(o["created_at"]) >= week_start]
    month_orders = [o for o in orders if parse_dt(o["created_at"]) >= month_start]

    # Item popularity
    item_counts = defaultdict(int)
    for o in orders:
        for item in o["items"]:
            item_counts[item["name"]] += item.get("qty", 1)

    sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
    top5 = sorted_items[:5]
    bottom5 = sorted_items[-5:][::-1]

    # Orders per hour (today)
    hourly = defaultdict(int)
    for o in today_orders:
        h = parse_dt(o["created_at"]).hour
        hourly[h] += 1
    orders_per_hour = [{"hour": h, "count": hourly.get(h, 0)} for h in range(24)]

    # Table usage
    table_usage = defaultdict(int)
    for o in orders:
        table_usage[o["table_number"]] += 1
    table_data = sorted([{"table": t, "orders": c} for t, c in table_usage.items()], key=lambda x: x["orders"], reverse=True)

    total = len(orders)
    avg = round(revenue(orders) / total, 2) if total > 0 else 0

    return {
        "revenue": {
            "today": revenue(today_orders),
            "week": revenue(week_orders),
            "month": revenue(month_orders),
            "all_time": revenue(orders)
        },
        "orders": {
            "today": len(today_orders),
            "week": len(week_orders),
            "month": len(month_orders),
            "total": total
        },
        "avg_order_value": avg,
        "popular_items": [{"name": n, "count": c} for n, c in top5],
        "least_ordered": [{"name": n, "count": c} for n, c in bottom5],
        "orders_per_hour": orders_per_hour,
        "table_usage": table_data
    }


@app.get("/export/csv")
def export_csv():
    conn = get_db()
    rows = conn.execute("SELECT * FROM orders ORDER BY created_at DESC").fetchall()
    conn.close()

    lines = ["id,table_number,items,total_price,status,created_at"]
    for r in rows:
        items_str = r["items"].replace(",", ";")
        lines.append(f'{r["id"]},{r["table_number"]},"{items_str}",{r["total_price"]},{r["status"]},{r["created_at"]}')

    content = "\n".join(lines)
    return StreamingResponse(
        io.StringIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders_export.csv"}
    )
