import secrets
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.dependencies import get_current_user_optional
from app.database import create_tables, get_db
from app.routers import admin, auth, cart, orders, products
from app.services import product_service


# Fix #9: 使用 lifespan 替代已弃用的 @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


# Fix #8: CSRF 中间件（双提交 Cookie 模式）
# GET 响应中自动种入 csrf_token cookie；POST 表单请求校验 cookie 与 hidden field 一致性
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type:
                raw_body = await request.body()
                form_data = parse_qs(raw_body.decode())
                form_token = (form_data.get("csrf_token") or [None])[0]
                cookie_token = request.cookies.get("csrf_token")

                if not form_token or not cookie_token or form_token != cookie_token:
                    return Response("CSRF 验证失败，请刷新页面后重试", status_code=403)

                # 回填 body，供后续路由正常消费
                async def _receive():
                    return {"type": "http.request", "body": raw_body, "more_body": False}

                request._receive = _receive

        response = await call_next(request)

        # 未携带 csrf_token cookie 时自动种入
        if "csrf_token" not in request.cookies:
            response.set_cookie(
                "csrf_token",
                secrets.token_hex(32),
                samesite="strict",
                httponly=False,
            )
        return response


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(CSRFMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)


# Fix #3: 使用依赖注入管理 Session 和当前用户，不再手动创建/关闭 Session
@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
) -> HTMLResponse:
    featured, _ = product_service.get_list(db, limit=8)
    categories = product_service.get_categories(db)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "featured": featured,
            "categories": categories,
            "current_user": current_user,
        },
    )
