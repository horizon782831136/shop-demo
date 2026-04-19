from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_optional
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> HTMLResponse:
    if current_user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "error": None, "current_user": None}
    )


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    try:
        token = auth_service.login(db, username, password)
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24)
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": str(e.detail if hasattr(e, "detail") else e), "current_user": None},
            status_code=401,
        )


@router.get("/register", response_class=HTMLResponse)
def register_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> HTMLResponse:
    if current_user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "error": None, "current_user": None}
    )


@router.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    try:
        auth_service.register(db, UserCreate(username=username, email=email, password=password))
        token = auth_service.login(db, username, password)
        response = RedirectResponse("/", status_code=302)
        response.set_cookie("access_token", token, httponly=True, max_age=60 * 60 * 24)
        return response
    except Exception as e:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": str(e.detail if hasattr(e, "detail") else e), "current_user": None},
            status_code=400,
        )


@router.get("/logout")
def logout() -> RedirectResponse:
    response = RedirectResponse("/auth/login", status_code=302)
    response.delete_cookie("access_token")
    return response
