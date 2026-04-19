# 电商网站项目需求与技术方案

## 一、项目概述

基于 Python + FastAPI 构建一个全栈电商平台，包含商品展示、购物车、订单管理、用户认证等核心功能。前端使用 Jinja2 模板 + TailwindCSS，数据库使用 SQLite（开发）。

---

## 二、功能需求

### 2.1 用户模块
- 用户注册 / 登录 / 登出
- JWT Token 认证
- 个人信息查看

### 2.2 商品模块
- 商品列表（分页、分类筛选、关键字搜索）
- 商品详情页
- 商品图片展示
- 库存状态显示

### 2.3 购物车模块
- 添加 / 删除 / 修改数量
- 购物车持久化（登录用户存数据库）
- 价格合计实时计算

### 2.4 订单模块
- 结算下单
- 订单列表（我的订单）
- 订单状态流转：待付款 → 已付款 → 已发货 → 已完成

### 2.5 后台管理（Admin）
- 商品增删改
- 订单状态更新
- 用户列表查看

---

## 三、技术方案

### 3.1 技术栈

| 层次 | 技术选型 |
|------|----------|
| Web 框架 | FastAPI |
| 模板引擎 | Jinja2 |
| 前端样式 | TailwindCSS CDN |
| ORM | SQLAlchemy 2.x |
| 数据库 | SQLite（文件：shop.db） |
| 认证 | JWT (python-jose) + passlib |
| 依赖管理 | pip + requirements.txt |

### 3.2 目录结构

```
shop-demo/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口，挂载路由
│   ├── database.py          # 数据库连接与 Session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   └── admin.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   └── order_service.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py        # 配置项
│   │   ├── security.py      # JWT、密码哈希
│   │   └── dependencies.py  # FastAPI 依赖注入
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── products/
│       │   ├── list.html
│       │   └── detail.html
│       ├── cart/
│       │   └── cart.html
│       ├── orders/
│       │   ├── checkout.html
│       │   └── list.html
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       └── admin/
│           ├── dashboard.html
│           ├── products.html
│           └── orders.html
├── static/
│   └── images/              # 商品占位图
├── requirements.txt
├── seed.py                  # 初始化测试数据
└── run.py                   # 启动入口
```

### 3.3 数据库模型

#### users
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| username | String(50) unique | 用户名 |
| email | String(100) unique | 邮箱 |
| hashed_password | String | 哈希密码 |
| is_admin | Boolean | 是否管理员 |
| created_at | DateTime | 注册时间 |

#### products
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| name | String(200) | 商品名 |
| description | Text | 描述 |
| price | Float | 价格 |
| stock | Integer | 库存 |
| category | String(50) | 分类 |
| image_url | String | 图片地址 |
| created_at | DateTime | |

#### cart_items
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| user_id | FK users | |
| product_id | FK products | |
| quantity | Integer | 数量 |

#### orders
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| user_id | FK users | |
| total_price | Float | 总价 |
| status | String | 订单状态 |
| created_at | DateTime | |

#### order_items
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | |
| order_id | FK orders | |
| product_id | FK products | |
| quantity | Integer | |
| unit_price | Float | 下单时快照价格 |

---

## 四、实施计划

### Phase 1：项目初始化
- [x] 生成 plan.md 和 CLAUDE.md
- [ ] 创建目录结构
- [ ] 编写 requirements.txt
- [ ] 配置 database.py 和 config.py

### Phase 2：模型与数据层
- [ ] 编写所有 SQLAlchemy 模型
- [ ] 编写 Pydantic schemas
- [ ] 编写 seed.py 初始化测试数据

### Phase 3：核心业务逻辑
- [ ] auth_service（注册、登录、JWT）
- [ ] product_service（列表、详情、搜索）
- [ ] cart_service（增删改购物车）
- [ ] order_service（下单、查询）

### Phase 4：路由层
- [ ] auth router（/auth/register, /auth/login, /auth/logout）
- [ ] products router（/products, /products/{id}）
- [ ] cart router（/cart, /cart/add, /cart/remove）
- [ ] orders router（/orders, /orders/checkout）
- [ ] admin router（/admin/*）

### Phase 5：前端模板
- [ ] base.html（导航栏、页脚）
- [ ] 首页 index.html
- [ ] 商品列表 / 详情
- [ ] 购物车页
- [ ] 结算 / 订单列表
- [ ] 登录 / 注册
- [ ] 后台管理页

### Phase 6：收尾
- [ ] run.py 启动脚本
- [ ] 功能自检
