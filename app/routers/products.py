from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user_optional
from app.database import get_db
from app.models.user import User
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"])
templates = Jinja2Templates(directory="app/templates")

PAGE_SIZE = 12


@router.get("", response_class=HTMLResponse)
def product_list(
    request: Request,
    category: str | None = None,
    keyword: str | None = None,
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> HTMLResponse:
    skip = (page - 1) * PAGE_SIZE
    items, total = product_service.get_list(db, category, keyword, skip, PAGE_SIZE)
    categories = product_service.get_categories(db)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    return templates.TemplateResponse(
        "products/list.html",
        {
            "request": request,
            "products": items,
            "categories": categories,
            "current_category": category,
            "keyword": keyword or "",
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "current_user": current_user,
        },
    )


@router.get("/{product_id}", response_class=HTMLResponse)
def product_detail(
    request: Request,
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
) -> HTMLResponse:
    product = product_service.get_by_id(db, product_id)
    return templates.TemplateResponse(
        "products/detail.html",
        {"request": request, "product": product, "current_user": current_user},
    )
