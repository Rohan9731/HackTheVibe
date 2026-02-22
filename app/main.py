"""
VibeShield — The Impulse Intelligence Layer
Main FastAPI application with per-user sessions.
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from app.database import init_db
from app.routers import transactions, mood, dashboard
from app.seed_data import seed_user_data

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="VibeShield", version="2.0")

# Static files & templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Include routers
app.include_router(transactions.router)
app.include_router(mood.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def startup():
    init_db()
    print("✅ VibeShield DB initialized (per-user isolation)")
    print("🚀 Open http://localhost:8000 to start")


# ─── Auth helpers ───

def _get_user(request: Request) -> tuple[str, str]:
    uid = request.cookies.get("vibeshield_user", "")
    name = request.cookies.get("vibeshield_name", "User")
    return uid, name


def _require_login(request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return None
    return uid


# ─── Login / Logout ───

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    uid, _ = _get_user(request)
    if uid:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/login")
async def do_login(request: Request):
    data = await request.json()
    username = data.get("username", "").strip()
    if not username:
        return {"error": "Please enter your name"}
    user_id = username.lower().replace(" ", "_").replace(".", "_")
    response = Response(content='{"status":"ok","redirect":"/"}',
                        media_type="application/json")
    response.set_cookie("vibeshield_user", user_id, max_age=86400, path="/")
    response.set_cookie("vibeshield_name", username, max_age=86400, path="/")
    return response


@app.get("/logout")
async def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie("vibeshield_user", path="/")
    response.delete_cookie("vibeshield_name", path="/")
    return response


# ─── Seed Demo Data ───

@app.post("/api/seed-demo")
async def seed_demo(request: Request):
    uid, _ = _get_user(request)
    if not uid:
        return {"error": "Not logged in"}
    from app.database import clear_user_data
    clear_user_data(uid)
    result = seed_user_data(uid, days=30)
    return {"status": "seeded", **result}


# ─── Page Routes ───

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    uid = _require_login(request)
    if not uid:
        return RedirectResponse("/login", status_code=302)
    _, name = _get_user(request)
    return templates.TemplateResponse("index.html", {
        "request": request, "user_name": name, "user_id": uid,
    })


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    uid = _require_login(request)
    if not uid:
        return RedirectResponse("/login", status_code=302)
    _, name = _get_user(request)
    return templates.TemplateResponse("dashboard.html", {
        "request": request, "user_name": name, "user_id": uid,
    })


@app.get("/triggers", response_class=HTMLResponse)
async def triggers_page(request: Request):
    uid = _require_login(request)
    if not uid:
        return RedirectResponse("/login", status_code=302)
    _, name = _get_user(request)
    return templates.TemplateResponse("triggers.html", {
        "request": request, "user_name": name, "user_id": uid,
    })


@app.get("/mood", response_class=HTMLResponse)
async def mood_page(request: Request):
    uid = _require_login(request)
    if not uid:
        return RedirectResponse("/login", status_code=302)
    _, name = _get_user(request)
    return templates.TemplateResponse("mood.html", {
        "request": request, "user_name": name, "user_id": uid,
    })
