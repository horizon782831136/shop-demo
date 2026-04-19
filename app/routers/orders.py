from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import cart_service, order_service

router = APIRouter(prefix="/orders", tags=["orders"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def order_list(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    orders = order_service.get_user_orders(db, current_user.id)
    return templates.TemplateResponse(
        "orders/list.html",
        {
            "request": request,
            "orders": orders,
            "status_labels": order_service.STATUS_LABELS,
            "current_user": current_user,
        },
    )


@router.get("/checkout", response_class=HTMLResponse)
def checkout_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    items, total = cart_service.get_cart(db, current_user.id)
    return templates.TemplateResponse(
        "orders/checkout.html",
        {"request": request, "items": items, "total": total, "current_user": current_user},
    )


@router.post("/checkout")
def do_checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RedirectResponse:
    order_service.checkout(db, current_user.id)
    return RedirectResponse("/orders", status_code=302)
