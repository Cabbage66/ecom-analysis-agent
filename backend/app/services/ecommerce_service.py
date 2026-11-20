from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.common.response import PageResponse
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review
from app.schemas.ecommerce import OrderItem, ProductItem, ReviewItem


def list_products(
    db: Session, page: int, page_size: int, keywords: str | None = None
) -> PageResponse:
    query = db.query(Product)
    if keywords and keywords.strip():
        keyword = f"%{keywords.strip()}%"
        query = query.filter(
            or_(Product.name.ilike(keyword), Product.category.ilike(keyword))
        )
    total = query.count()
    rows = (
        query.order_by(Product.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse(
        list=[ProductItem.model_validate(product) for product in rows], total=total
    )


def list_orders(
    db: Session, page: int, page_size: int, keywords: str | None = None
) -> PageResponse:
    query = db.query(Order, Product.name.label("product_name")).outerjoin(
        Product, Order.product_id == Product.id
    )
    if keywords and keywords.strip():
        keyword = f"%{keywords.strip()}%"
        query = query.filter(
            or_(
                Order.order_no.ilike(keyword),
                Order.buyer_name.ilike(keyword),
                Product.name.ilike(keyword),
            )
        )
    total = query.count()
    rows = (
        query.order_by(Order.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse(
        list=[
            OrderItem.model_validate(order).model_copy(
                update={"product_name": product_name}
            )
            for order, product_name in rows
        ],
        total=total,
    )


def list_reviews(
    db: Session, page: int, page_size: int, keywords: str | None = None
) -> PageResponse:
    query = db.query(Review, Product.name.label("product_name")).outerjoin(
        Product, Review.product_id == Product.id
    )
    if keywords and keywords.strip():
        keyword = f"%{keywords.strip()}%"
        query = query.filter(
            or_(Review.content.ilike(keyword), Product.name.ilike(keyword))
        )
    total = query.count()
    rows = (
        query.order_by(Review.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PageResponse(
        list=[
            ReviewItem.model_validate(review).model_copy(
                update={"product_name": product_name}
            )
            for review, product_name in rows
        ],
        total=total,
    )
