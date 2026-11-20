from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.common.response import Response
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import ecommerce_service

router = APIRouter(prefix="/ecommerce", tags=["电商业务数据（只读）"])


@router.get("/products")
def get_products(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    """分页查询商品"""
    return Response.success(
        data=ecommerce_service.list_products(
            db=db, page=page, page_size=page_size, keywords=keywords
        )
    )


@router.get("/orders")
def get_orders(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    """分页查询订单"""
    return Response.success(
        data=ecommerce_service.list_orders(
            db=db, page=page, page_size=page_size, keywords=keywords
        )
    )


@router.get("/reviews")
def get_reviews(
    _user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 10,
    keywords: str | None = None,
):
    """分页查询评价"""
    return Response.success(
        data=ecommerce_service.list_reviews(
            db=db, page=page, page_size=page_size, keywords=keywords
        )
    )
