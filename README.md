# ShopDemo — FastAPI 全栈电商平台

基于 **FastAPI + SQLAlchemy 2.x + Jinja2 + TailwindCSS** 构建的全栈电商演示项目，涵盖用户认证、商品管理、购物车、订单流转和后台管理五大核心模块。

---

## 功能概览

| 模块 | 功能点 |
|------|--------|
| 用户认证 | 注册 / 登录 / 登出，JWT Token（HttpOnly Cookie） |
| 商品浏览 | 列表分页、分类筛选、关键字搜索、商品详情 |
| 购物车 | 添加 / 修改数量 / 删除，价格实时合计，登录用户数据库持久化 |
| 订单 | 一键结算、我的订单列表、状态流转（待付款→已付款→已发货→已完成） |
| 后台管理 | 商品增删改、订单状态更新（需管理员权限） |

---

## 技术栈

| 层次 | 选型 |
|------|------|
| Web 框架 | FastAPI 0.111 |
| 模板引擎 | Jinja2 3.1 |
| 前端样式 | TailwindCSS CDN |
| ORM | SQLAlchemy 2.0（`Mapped` / `mapped_column` 风格） |
| 数据库 | SQLite（开发）；可替换为任意 SQLAlchemy 支持的数据库 |
| 认证 | JWT（python-jose）+ bcrypt 密码哈希（passlib） |
| 配置管理 | pydantic-settings，支持 `.env` 覆盖 |
| 运行服务器 | Uvicorn |

---

## 目录结构

```
shop-demo/
├── app/
│   ├── main.py              # FastAPI 入口，路由挂载，首页
│   ├── database.py          # 数据库引擎、Session、Base
│   ├── models/              # SQLAlchemy 数据模型
│   │   ├── user.py          # User
│   │   ├── product.py       # Product
│   │   ├── cart.py          # CartItem
│   │   └── order.py         # Order / OrderItem
│   ├── schemas/             # Pydantic 输入/输出模型
│   │   ├── user.py          # UserBase / UserCreate / UserOut
│   │   ├── product.py       # ProductBase / ProductCreate / ProductOut
│   │   ├── cart.py          # CartItemOut
│   │   └── order.py         # OrderOut / OrderItemOut
│   ├── services/            # 业务逻辑层（路由不直接操作 DB）
│   │   ├── auth_service.py  # 注册、登录、JWT 签发
│   │   ├── product_service.py  # 列表、搜索、CRUD
│   │   ├── cart_service.py  # 购物车增删改查
│   │   └── order_service.py # 结算、状态流转
│   ├── routers/             # FastAPI 路由（HTTP 层）
│   │   ├── auth.py          # /auth/*
│   │   ├── products.py      # /products/*
│   │   ├── cart.py          # /cart/*
│   │   ├── orders.py        # /orders/*
│   │   └── admin.py         # /admin/*
│   ├── core/
│   │   ├── config.py        # Settings（pydantic-settings）
│   │   ├── security.py      # 密码哈希 / JWT 编解码
│   │   └── dependencies.py  # get_current_user / require_admin
│   └── templates/           # Jinja2 HTML 模板
│       ├── base.html        # 公共导航、布局
│       ├── index.html       # 首页（精选商品）
│       ├── products/        # 商品列表、详情
│       ├── cart/            # 购物车页
│       ├── orders/          # 结算页、订单列表
│       ├── auth/            # 登录、注册
│       └── admin/           # 后台看板、商品管理、订单管理
├── seed.py                  # 初始化测试数据
├── run.py                   # 启动入口
├── requirements.txt
└── .gitignore
```

---

## 数据库模型

```
users
  id | username | email | hashed_password | is_admin | created_at

products
  id | name | description | price | stock | category | image_url | created_at

cart_items
  id | user_id(FK) | product_id(FK) | quantity

orders
  id | user_id(FK) | total_price | status | created_at
  status: pending → paid → shipped → completed

order_items
  id | order_id(FK) | product_id(FK) | quantity | unit_price（下单快照价格）
```

---

## 快速开始

### 1. 安装依赖

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 初始化测试数据

```bash
python seed.py
```

创建以下账号及 8 件示例商品（手机、电脑、耳机、平板）：

| 账号 | 密码 | 角色 |
|------|------|------|
| admin | admin123 | 管理员 |
| test | test123 | 普通用户 |

### 3. 启动服务

```bash
python run.py
```

访问 [http://localhost:8000](http://localhost:8000)

---

## 环境变量配置

项目根目录创建 `.env` 文件（可选，覆盖默认值）：

```env
SECRET_KEY=your-production-secret-key
DATABASE_URL=sqlite:///./shop.db
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

> 生产环境必须替换 `SECRET_KEY`，禁止使用默认开发值。

---

## 路由一览

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/` | 首页（精选商品） | 公开 |
| GET | `/products` | 商品列表（分页/筛选/搜索） | 公开 |
| GET | `/products/{id}` | 商品详情 | 公开 |
| GET/POST | `/auth/login` | 登录 | 公开 |
| GET/POST | `/auth/register` | 注册 | 公开 |
| GET | `/auth/logout` | 登出 | 登录用户 |
| GET | `/cart` | 购物车 | 登录用户 |
| POST | `/cart/add` | 加入购物车 | 登录用户 |
| POST | `/cart/update/{id}` | 修改数量 | 登录用户 |
| POST | `/cart/remove/{id}` | 删除购物车条目 | 登录用户 |
| GET/POST | `/orders/checkout` | 结算 | 登录用户 |
| GET | `/orders` | 我的订单 | 登录用户 |
| GET | `/admin` | 后台看板 | 管理员 |
| GET | `/admin/products` | 商品管理 | 管理员 |
| POST | `/admin/products/create` | 新建商品 | 管理员 |
| POST | `/admin/products/{id}/update` | 更新商品 | 管理员 |
| POST | `/admin/products/{id}/delete` | 删除商品 | 管理员 |
| GET | `/admin/orders` | 所有订单 | 管理员 |
| POST | `/admin/orders/{id}/status` | 更新订单状态 | 管理员 |

---

## 架构设计要点

- **分层架构**：`router → service → model`，路由层只负责 HTTP 参数解析与响应，业务逻辑全部收敛到 `services/`。
- **依赖注入**：`get_current_user`、`require_admin`、`get_db` 统一在 `core/dependencies.py` 管理，路由声明式使用 `Depends()`。
- **认证机制**：JWT Token 存储于 HttpOnly Cookie（key: `access_token`），有效期 24 小时，防止 XSS 读取。
- **价格快照**：下单时将 `unit_price` 写入 `order_items`，避免后续商品调价影响历史订单金额。
- **安全**：密码使用 bcrypt 哈希，禁止明文存储；SQL 查询全部通过 ORM，杜绝注入；管理员路由通过 `require_admin` 依赖强制鉴权。
