# 🍽 TableOrder — Digital Restaurant Ordering System

A full-stack restaurant management system with QR-based table ordering, live reception dashboard, and analytics.

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py              # FastAPI backend (all endpoints)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── customer.html        # 📱 Customer menu (mobile-first)
│   ├── admin.html           # 🖥  Reception dashboard
│   ├── analytics.html       # 📊 Analytics dashboard
│   └── qr_print.html        # 🖨  QR code print sheet
├── database/
│   └── orders.db            # SQLite database (auto-created)
├── qr_codes/                # Generated QR PNG files
├── serve_frontend.py        # Simple Python static server
└── start.sh                 # One-command startup script
```

---

## 🚀 Quick Start (Local)

### Step 1 — Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Start the backend (FastAPI)

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Step 3 — Serve the frontend

```bash
# From the project root
python3 serve_frontend.py
```

### Or: One-command startup

```bash
chmod +x start.sh
./start.sh
```

---

## 🌐 URLs (Local)

| Page | URL |
|------|-----|
| 📱 Customer Menu (Table 1) | http://localhost:8080/customer.html?table=1 |
| 🖥  Reception Dashboard | http://localhost:8080/admin.html |
| 📊 Analytics | http://localhost:8080/analytics.html |
| 🖨  QR Print Sheet | http://localhost:8080/qr_print.html |
| 🔌 API Docs | http://localhost:8000/docs |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/order` | Place new order |
| GET | `/orders` | Get all orders |
| GET | `/orders/{table}` | Get specific table order |
| DELETE | `/order/{table}` | Clear table |
| PATCH | `/order/{table}/status?status=served` | Update status |
| GET | `/analytics` | Get analytics data |
| GET | `/generate_qr/{table}?base_url=...` | Generate QR code |
| GET | `/export/csv` | Export all orders as CSV |

---

## ☁️ Hosting Online

### Backend → Render or Railway

1. Push `backend/` to a GitHub repo
2. Create a new Web Service on [Render](https://render.com) or [Railway](https://railway.app)
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Note your backend URL: e.g. `https://tableorder-api.onrender.com`

### Frontend → Vercel / Netlify / GitHub Pages

1. Push `frontend/` to a GitHub repo
2. Connect to [Vercel](https://vercel.com) or [Netlify](https://netlify.com)
3. No build step needed — just static files

### Connect Frontend to Backend

In each HTML file, before the closing `</body>` tag add:

```html
<script>
  window.API_BASE = 'https://your-backend-url.onrender.com';
</script>
```

Or set it in a shared `config.js` file:

```js
// config.js
window.API_BASE = 'https://your-backend-url.onrender.com';
```

And include it in each HTML:
```html
<script src="config.js"></script>
```

### QR Codes for Production

When generating QR codes, use your hosted frontend URL:

```
GET https://your-api.onrender.com/generate_qr/1?base_url=https://your-frontend.vercel.app
```

---

## 🍽 Menu Customization

The menu is defined in `frontend/customer.html` inside the `MENU` object. Edit items, prices, categories, emojis, and tags there:

```js
const MENU = {
  "Starters": [
    { id: 1, name: "Chicken Momo", price: 180, emoji: "🥟",
      desc: "Steamed dumplings", tags: ["spicy"] },
    // ...
  ],
  // Add more categories...
};
```

---

## 🔧 Configuration

- **Number of tables** in reception dashboard: Change `const TABLES = 12;` in `admin.html`
- **Polling interval**: Change `setInterval(fetchOrders, 3000)` (in ms)
- **Currency**: Search and replace `Rs.` with your currency symbol

---

## ✨ Features Summary

- ✅ QR code per table — downloadable PNG
- ✅ Mobile-first customer menu with live cart
- ✅ Reception dashboard with real-time polling
- ✅ Sound alerts for new orders
- ✅ Mark orders as Served / Clear table
- ✅ Analytics: revenue, top items, peak hours, table usage
- ✅ Orders per hour bar chart + popular items pie chart
- ✅ CSV export of all orders
- ✅ QR print sheet for all tables
- ✅ Hosting-ready (Render + Vercel)

---

## 📦 Tech Stack

| Layer | Tech |
|-------|------|
| Frontend | HTML5, CSS3, Vanilla JS |
| Charts | Chart.js 4 |
| Backend | Python + FastAPI |
| Database | SQLite |
| QR Codes | qrcode + Pillow |

---

*Built for small-to-medium restaurants. Handles 4–50 orders per 5 minutes comfortably.*
