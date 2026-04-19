from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.dependencies import get_current_user_optional
from app.database import create_tables
from app.routers import admin, auth, cart, orders, products

app = FastAPI(title=settings.APP_NAME)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup() -> None:
    create_tables()


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    from app.database import SessionLocal
    from app.services import product_service

    db = SessionLocal()
    try:
        featured, _ = product_service.get_list(db, limit=8)
        categories = product_service.get_categories(db)
        current_user = get_current_user_optional(
            request.cookies.get("access_token"), db
        )
    finally:
        db.close()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "featured": featured,
            "categories": categories,
            "current_user": current_user,
        },
    )
