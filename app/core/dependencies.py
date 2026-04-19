from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not access_token:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token 无效")
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_current_user_optional(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not access_token:
        return None
    payload = decode_access_token(access_token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    return db.get(User, int(user_id))


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
