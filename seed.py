"""初始化测试数据脚本"""
from app.core.security import hash_password
from app.database import SessionLocal, create_tables
from app.models.product import Product
from app.models.user import User

PRODUCTS = [
    {
        "name": "Apple iPhone 15 Pro",
        "description": "最新款苹果手机，A17 Pro 芯片，钛金属机身",
        "price": 8999.0,
        "stock": 50,
        "category": "手机",
        "image_url": "https://picsum.photos/seed/iphone/400/400",
    },
    {
        "name": "Samsung Galaxy S24",
        "description": "三星旗舰手机，骁龙8 Gen3，200MP 摄像头",
        "price": 6999.0,
        "stock": 30,
        "category": "手机",
        "image_url": "https://picsum.photos/seed/samsung/400/400",
    },
    {
        "name": "MacBook Pro 14寸",
        "description": "Apple M3 Pro 芯片，18GB 内存，512GB SSD",
        "price": 14999.0,
        "stock": 20,
        "category": "电脑",
        "image_url": "https://picsum.photos/seed/macbook/400/400",
    },
    {
        "name": "戴尔 XPS 15",
        "description": "OLED 屏幕，Intel i7，RTX 4060，32GB 内存",
        "price": 12999.0,
        "stock": 15,
        "category": "电脑",
        "image_url": "https://picsum.photos/seed/dell/400/400",
    },
    {
        "name": "索尼 WH-1000XM5",
        "description": "旗舰降噪耳机，30小时续航，多设备连接",
        "price": 2499.0,
        "stock": 100,
        "category": "耳机",
        "image_url": "https://picsum.photos/seed/sony/400/400",
    },
    {
        "name": "AirPods Pro 2",
        "description": "主动降噪，透明模式，空间音频，H2芯片",
        "price": 1899.0,
        "stock": 80,
        "category": "耳机",
        "image_url": "https://picsum.photos/seed/airpods/400/400",
    },
    {
        "name": "iPad Air M2",
        "description": "M2 芯片，11寸液晶屏，支持 Apple Pencil",
        "price": 4799.0,
        "stock": 40,
        "category": "平板",
        "image_url": "https://picsum.photos/seed/ipad/400/400",
    },
    {
        "name": "华为 MateBook X Pro",
        "description": "3K 触控屏，Ultra 7 处理器，1kg 轻薄机身",
        "price": 9999.0,
        "stock": 25,
        "category": "电脑",
        "image_url": "https://picsum.photos/seed/huawei/400/400",
    },
]


def seed() -> None:
    create_tables()
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                username="admin",
                email="admin@shop.com",
                hashed_password=hash_password("admin123"),
                is_admin=True,
            )
            user = User(
                username="test",
                email="test@shop.com",
                hashed_password=hash_password("test123"),
                is_admin=False,
            )
            db.add_all([admin, user])
            db.commit()
            print("创建用户：admin / admin123，test / test123")

        if db.query(Product).count() == 0:
            for p in PRODUCTS:
                db.add(Product(**p))
            db.commit()
            print(f"创建 {len(PRODUCTS)} 件商品")

        print("数据初始化完成")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
