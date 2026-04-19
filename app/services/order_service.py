from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.services import cart_service

VALID_STATUSES = {"pending", "paid", "shipped", "completed"}
STATUS_LABELS = {
    "pending": "待付款",
    "paid": "已付款",
    "shipped": "已发货",
    "completed": "已完成",
}


def checkout(db: Session, user_id: int) -> Order:
    cart_items, total = cart_service.get_cart(db, user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车为空")
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise HTTPException(
                status_code=400, detail=f"商品「{item.product.name}」库存不足"
            )
    order = Order(user_id=user_id, total_price=total, status="pending")
    db.add(order)
    db.flush()
    for item in cart_items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
        )
        item.product.stock -= item.quantity
    db.commit()
    db.refresh(order)
    cart_service.clear_cart(db, user_id)
    return order


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )


def get_all_orders(db: Session) -> list[Order]:
    return db.query(Order).order_by(Order.created_at.desc()).all()


def get_by_id(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


def update_status(db: Session, order_id: int, status: str) -> Order:
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"无效状态，可选：{VALID_STATUSES}")
    order = get_by_id(db, order_id)
    order.status = status
    db.commit()
    db.refresh(order)
    return order
