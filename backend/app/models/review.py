from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Review(Base):
    """评价表"""

    __tablename__ = "reviews"
    __table_args__ = (
        Index("idx_reviews_product_id", "product_id"),
        Index("idx_reviews_order_id", "order_id"),
        {"comment": "评价表"},
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", name="fk_reviews_product"),
        nullable=False, comment="商品ID"
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", name="fk_reviews_order"),
        nullable=True, comment="关联订单ID"
    )
    rating: Mapped[int] = mapped_column(nullable=False, comment="评分1-5")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="评价正文")
    img: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="评价图片相对路径"
    )
