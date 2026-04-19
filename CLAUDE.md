# CLAUDE.md — 项目代码生成规范

本文件约束所有代码生成行为，必须严格遵守。

---

## 1. 通用规范

- **语言版本**：Python 3.11+，使用类型注解（Type Hints）
- **编码风格**：遵循 PEP 8，缩进 4 空格，不使用 Tab
- **行长度**：最大 100 字符
- **命名规范**
  - 模块、变量、函数：`snake_case`
  - 类名：`PascalCase`
  - 常量：`UPPER_SNAKE_CASE`
  - 私有成员：`_single_leading_underscore`
- **禁止使用** `*` 导入（`from module import *`）
- **导入顺序**：标准库 → 第三方库 → 本地模块，各组之间空一行

---

## 2. FastAPI 规范

- 所有路由函数必须声明返回类型或 `response_model`
- 路由函数只负责 HTTP 层（参数解析、调用 service、返回响应），不写业务逻辑
- 路径参数、查询参数均使用 FastAPI 原生声明，不手动解析 `request`
- 依赖注入（`Depends`）统一放在 `app/core/dependencies.py`
- 异常统一使用 `HTTPException`，状态码语义要正确
- 路由前缀和 tag 在各 router 文件内定义，不在 main.py 硬编码

```python
# 示例：正确的路由写法
@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductOut:
    return product_service.get_by_id(db, product_id)
```

---

## 3. SQLAlchemy 规范

- 使用 SQLAlchemy 2.x 风格（`mapped_column`、`Mapped`）
- 所有模型继承自统一 `Base = declarative_base()`，定义在 `app/database.py`
- 外键关系必须定义 `relationship`，并指定 `back_populates`
- 禁止在模型层执行业务逻辑，模型只描述结构
- Session 生命周期由依赖注入管理，不手动 `session.close()`

```python
# 示例：正确的模型写法
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
```

---

## 4. Pydantic Schemas 规范

- 按职责拆分：`XxxBase`（公共字段）、`XxxCreate`（创建入参）、`XxxOut`（响应出参）
- 响应 schema 必须设置 `model_config = ConfigDict(from_attributes=True)`
- 不在 schema 中写数据库查询或业务逻辑
- 密码字段只存在于 `XxxCreate` 中，`XxxOut` 中不返回密码

---

## 5. Service 层规范

- 所有业务逻辑（查询、计算、状态变更）写在 `services/` 中
- Service 函数第一个参数是 `db: Session`，其余是业务参数
- 函数须有明确的返回类型注解
- 查不到资源时 raise `HTTPException(status_code=404)`
- 权限不足时 raise `HTTPException(status_code=403)`
- 同一 service 文件内的函数可互相调用，跨模块调用需通过参数传入，不直接 import 其他 service

---

## 6. 模板规范

- 所有页面继承 `base.html`，使用 `{% extends "base.html" %}`
- 动态数据通过 `TemplateResponse` context 传入，不在模板中写 Python 逻辑
- 表单使用 `<form method="post">` + CSRF 意识（本项目暂用 hidden field token 占位）
- TailwindCSS 使用 CDN 引入，不本地构建
- 错误消息通过 flash message 机制（session）显示

---

## 7. 安全规范

- 密码必须使用 `passlib[bcrypt]` 哈希，禁止明文存储
- JWT secret 从环境变量 `SECRET_KEY` 读取，有默认开发值
- 管理员路由必须校验 `current_user.is_admin`
- SQL 查询必须通过 ORM，禁止拼接原始 SQL 字符串
- 用户输入经 Pydantic 校验后再使用

---

## 8. 文件与模块规范

- 每个 `__init__.py` 保持空文件或仅做必要导出
- `app/core/config.py` 使用 `pydantic-settings` 管理配置，支持 `.env` 覆盖
- `run.py` 只做启动，不含业务代码：

```python
import uvicorn
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 9. 禁止事项

- 禁止在路由函数中直接操作 DB（必须经过 service）
- 禁止硬编码端口、密钥、数据库路径到业务代码中（放 config）
- 禁止生成测试文件、Dockerfile、CI 配置（除非用户明确要求）
- 禁止添加未被需求覆盖的功能
- 禁止生成注释说明已删除的代码

---

## 10. requirements.txt 标准

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
pydantic==2.7.1
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
jinja2==3.1.4
python-multipart==0.0.9
aiofiles==23.2.1
```
