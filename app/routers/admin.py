from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import order_service, product_service

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> HTMLResponse:
    products, product_count = product_service.get_list(db, limit=1000)
    orders = order_service.get_all_orders(db)
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "product_count": product_count,
            "order_count": len(orders),
            "current_user": current_user,
        },
    )


@router.get("/products", response_class=HTMLResponse)
def admin_products(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> HTMLResponse:
    products, _ = product_service.get_list(db, limit=1000)
    categories = product_service.get_categories(db)
    return templates.TemplateResponse(
        "admin/products.html",
        {"request": request, "products": products, "categories": categories, "current_user": current_user},
    )


@router.post("/products/create")
def admin_create_product(
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    stock: int = Form(0),
    category: str = Form("other"),
    image_url: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RedirectResponse:
    product_service.create(
        db,
        ProductCreate(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image_url=image_url,
        ),
    )
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/{product_id}/update")
def admin_update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    stock: int = Form(None),
    category: str = Form(None),
    image_url: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RedirectResponse:
    product_service.update(
        db,
        product_id,
        ProductUpdate(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image_url=image_url,
        ),
    )
    return RedirectResponse("/admin/products", status_code=302)


@router.post("/products/{product_id}/delete")
def admin_delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RedirectResponse:
    product_service.delete(db, product_id)
    return RedirectResponse("/admin/products", status_code=302)


@router.get("/orders", response_class=HTMLResponse)
def admin_orders(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> HTMLResponse:
    orders = order_service.get_all_orders(db)
    return templates.TemplateResponse(
        "admin/orders.html",
        {
            "request": request,
            "orders": orders,
            "status_labels": order_service.STATUS_LABELS,
            "current_user": current_user,
        },
    )


@router.post("/orders/{order_id}/status")
def admin_update_order_status(
    order_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> RedirectResponse:
    order_service.update_status(db, order_id, status)
    return RedirectResponse("/admin/orders", status_code=302)
