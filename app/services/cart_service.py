from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product


def get_cart(db: Session, user_id: int) -> tuple[list[CartItem], float]:
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .join(CartItem.product)
        .all()
    )
    total = sum(item.product.price * item.quantity for item in items)
    return items, total


def add_item(db: Session, user_id: int, product_id: int, quantity: int) -> CartItem:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    existing = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id, CartItem.product_id == product_id)
        .first()
    )
    if existing:
        new_qty = existing.quantity + quantity
        if product.stock < new_qty:
            raise HTTPException(status_code=400, detail="库存不足")
        existing.quantity = new_qty
        db.commit()
        db.refresh(existing)
        return existing
    item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_quantity(db: Session, user_id: int, item_id: int, quantity: int) -> CartItem:
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    if item.product.stock < quantity:
        raise HTTPException(status_code=400, detail="库存不足")
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def remove_item(db: Session, user_id: int, item_id: int) -> None:
    item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == user_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    db.delete(item)
    db.commit()


def clear_cart(db: Session, user_id: int) -> None:
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
