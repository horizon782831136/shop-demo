from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.services import cart_service

STATUS_LABELS = {
    "pending": "待付款",
    "paid": "已付款",
    "shipped": "已发货",
    "completed": "已完成",
}

# Fix #5: 合法状态流转映射，禁止逆向或跳级变更
_VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"paid"},
    "paid": {"shipped"},
    "shipped": {"completed"},
    "completed": set(),
}


def checkout(db: Session, user_id: int) -> Order:
    cart_items, total = cart_service.get_cart(db, user_id)
    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车为空")

    product_ids = [item.product_id for item in cart_items]
    # Fix #1: 用 with_for_update() 加行级锁，防止并发超卖
    locked_products: dict[int, Product] = {
        p.id: p
        for p in db.query(Product)
        .filter(Product.id.in_(product_ids))
        .with_for_update()
        .all()
    }

    for item in cart_items:
        product = locked_products[item.product_id]
        if product.stock < item.quantity:
            db.rollback()
            raise HTTPException(
                status_code=400, detail=f"商品「{product.name}」库存不足"
            )

    order = Order(user_id=user_id, total_price=total, status="pending")
    db.add(order)
    db.flush()

    for item in cart_items:
        product = locked_products[item.product_id]
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=product.price,
            )
        )
        product.stock -= item.quantity

    # Fix #4: 清空购物车与创建订单在同一事务内，保证原子性
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    db.refresh(order)
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
    order = get_by_id(db, order_id)
    allowed = _VALID_TRANSITIONS.get(order.status, set())
    # Fix #5: 校验状态流转合法性，禁止逆序或跳级变更
    if status not in allowed:
        labels = {k: STATUS_LABELS[k] for k in allowed} if allowed else {}
        detail = (
            f"当前状态「{STATUS_LABELS.get(order.status, order.status)}」"
            f"不允许变更为「{STATUS_LABELS.get(status, status)}」"
            + (f"，可变更为：{list(labels.values())}" if labels else "（终态，不可变更）")
        )
        raise HTTPException(status_code=400, detail=detail)
    order.status = status
    db.commit()
    db.refresh(order)
    return order
