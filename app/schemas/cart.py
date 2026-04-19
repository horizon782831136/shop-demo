from pydantic import BaseModel, ConfigDict, Field

from app.schemas.product import ProductOut


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, default=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    product: ProductOut


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float
