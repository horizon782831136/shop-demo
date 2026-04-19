from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def cart_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    items, total = cart_service.get_cart(db, current_user.id)
    return templates.TemplateResponse(
        "cart/cart.html",
        {"request": request, "items": items, "total": total, "current_user": current_user},
    )


@router.post("/add")
def add_to_cart(
    product_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    cart_service.add_item(db, current_user.id, product_id, quantity)
    return RedirectResponse("/cart", status_code=302)


@router.post("/update/{item_id}")
def update_cart_item(
    item_id: int,
    quantity: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    cart_service.update_quantity(db, current_user.id, item_id, quantity)
    return RedirectResponse("/cart", status_code=302)


@router.post("/remove/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    cart_service.remove_item(db, current_user.id, item_id)
    return RedirectResponse("/cart", status_code=302)
