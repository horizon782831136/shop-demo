from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def get_list(
    db: Session,
    category: str | None = None,
    keyword: str | None = None,
    skip: int = 0,
    limit: int = 12,
) -> tuple[list[Product], int]:
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        query = query.filter(Product.name.ilike(f"%{keyword}%"))
    total = query.count()
    items = query.order_by(Product.id.desc()).offset(skip).limit(limit).all()
    return items, total


def get_by_id(db: Session, product_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return product


def get_categories(db: Session) -> list[str]:
    rows = db.query(Product.category).distinct().all()
    return [r[0] for r in rows]


def create(db: Session, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_by_id(db, product_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def delete(db: Session, product_id: int) -> None:
    product = get_by_id(db, product_id)
    db.delete(product)
    db.commit()
