# TableOrder

A simple restaurant ordering system with:

- FastAPI backend
- static frontend pages
- SQLite storage
- QR code generation for tables

## Project Structure

```text
menu/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── requirements.txt
│   ├── data/
│   │   └── orders.db
│   └── generated/
│       └── qr_codes/
├── frontend/
│   ├── admin.html
│   ├── analytics.html
│   ├── config.js
│   ├── customer.html
│   ├── qr_print.html
│   └── serve_frontend.py
├── .gitignore
├── README.md
└── start.sh
```

## Local Run

Install dependencies:

```bash
python3 -m pip install -r backend/requirements.txt
```

Run the backend:

```bash
python3 -m uvicorn backend.main:app --reload --port 8000
```

Run the frontend:

```bash
python3 frontend/serve_frontend.py
```

Or start both:

```bash
chmod +x start.sh
./start.sh
```

## Local URLs

- Customer menu: `http://localhost:8080/customer.html?table=1`
- Reception: `http://localhost:8080/admin.html`
- Analytics: `http://localhost:8080/analytics.html`
- QR print sheet: `http://localhost:8080/qr_print.html`
- API docs: `http://localhost:8000/docs`

## Deploy Backend on Render

The backend is ready for Render with SQLite stored on a persistent disk.

Files:

- [render.yaml](/Users/bishnuprasadtiwari/Desktop/menu/render.yaml:1)
- [backend/main.py](/Users/bishnuprasadtiwari/Desktop/menu/backend/main.py:1)

Steps:

1. Push this repo to GitHub.
2. In Render, create a new `Blueprint` or `Web Service` from the repo.
3. Use these settings:
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/healthz`
4. Attach a persistent disk.
5. Set:
   - `TABLEORDER_DATA_DIR=/opt/render/project/src/var/data`
   - `TABLEORDER_GENERATED_DIR=/opt/render/project/src/var/generated`
6. Deploy and copy the backend URL.

Example backend URL:

```text
https://tableorder-api.onrender.com
```

## Deploy Frontend on Vercel

The frontend is a plain static site in `frontend/`.

Files:

- [frontend/config.js](/Users/bishnuprasadtiwari/Desktop/menu/frontend/config.js:1)
- [frontend/vercel.json](/Users/bishnuprasadtiwari/Desktop/menu/frontend/vercel.json:1)

Steps:

1. In Vercel, create a new project from the same repo.
2. Set the project `Root Directory` to `frontend`.
3. No build command is required.
4. Before deploying, update [frontend/config.js](/Users/bishnuprasadtiwari/Desktop/menu/frontend/config.js:1) so production points to your Render backend URL:

```js
window.TABLEORDER_API_BASE = "https://tableorder-api.onrender.com";
```

Add that line above the IIFE, or replace the placeholder fallback string.

5. Deploy.

Your frontend URLs will look like:

- `https://your-project.vercel.app/customer.html?table=1`
- `https://your-project.vercel.app/admin.html`
- `https://your-project.vercel.app/analytics.html`

## Recommended Order

1. Deploy backend on Render first.
2. Copy the real Render URL.
3. Put that URL into `frontend/config.js`.
4. Deploy frontend on Vercel.

## Notes

- SQLite needs persistent storage on Render. Without a disk, data will be lost on redeploy/restart.
- Local development still uses frontend on `:8080` and backend on `:8000`.
