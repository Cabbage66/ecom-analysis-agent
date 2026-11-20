from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_serializer


class ProductItem(BaseModel):
    id: int
    name: str
    category: str
    description: str
    price: Decimal
    stock: int
    shelf_status: str
    review_status: str
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("price")
    def _price_to_float(self, v: Decimal) -> float:
        return float(v)

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class OrderItem(BaseModel):
    id: int
    order_no: str
    product_id: int
    product_name: str | None = None
    buyer_name: str
    quantity: int
    amount: Decimal
    status: str
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("amount")
    def _amount_to_float(self, v: Decimal) -> float:
        return float(v)

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None


class ReviewItem(BaseModel):
    id: int
    product_id: int
    product_name: str | None = None
    order_id: int | None = None
    rating: int
    content: str
    img: str | None = None
    create_time: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("create_time")
    def _time(self, v: datetime | None) -> str | None:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else None
