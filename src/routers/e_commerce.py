from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.ecommerce_database import get_ecom_db
from src.load_products import load_products
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import datetime

from src.core.ecommerce_database import get_ecom_db
from src.models.ecommerce_models import Product, ProductTag, Review, Dimensions, Meta


router = APIRouter(
    prefix="/products",
    tags=["products"],
    responses={400: {"detail": "Bad request"}},
)


@router.post("/sync-products")
def sync_products():
    load_products()
    return {"message": "Products synced"}


@router.post("/query")
def execute_sql_query(
    sqlquery: str,
    db: Session = Depends(get_ecom_db),
):
    """
    Execute read-only SQL queries on ecommerce DB.
    Supports JOIN, GROUP BY, ORDER BY, etc.
    """

    sql_lower = sqlquery.strip().lower()

    if not sql_lower.startswith("select"):
        raise HTTPException(
            status_code=400,
            detail="Only SELECT queries are allowed",
        )

    dangerous_statements = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "truncate ",
        "create table",
        "replace ",
    ]

    if any(stmt in sql_lower for stmt in dangerous_statements):
        raise HTTPException(
            status_code=400,
            detail="Dangerous SQL detected",
        )

    try:
        result = db.execute(text(sqlquery))
        rows = result.fetchall()
        columns = result.keys()

        data = [dict(zip(columns, row)) for row in rows]

        return {
            "row_count": len(data),
            "columns": list(columns),
            "data": data,
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def serialize_product(p: Product):
    return {
        "id": p.id,
        "title": p.title,
        "price": p.price,
        "rating": p.rating,
        "stock": p.stock,
        "brand": p.brand,
        "category": p.category,
        "thumbnail": p.thumbnail,
        "dimensions": (
            {
                "width": p.dimensions.width if p.dimensions else None,
                "height": p.dimensions.height if p.dimensions else None,
                "depth": p.dimensions.depth if p.dimensions else None,
            }
            if p.dimensions
            else None
        ),
        "meta": (
            {
                "barcode": p.meta.barcode if p.meta else None,
                "created_at": p.meta.created_at if p.meta else None,
            }
            if p.meta
            else None
        ),
        "tags": [t.tag for t in p.tags],
        "images": [i.url for i in p.images],
        "reviews": [
            {
                "rating": r.rating,
                "comment": r.comment,
                "reviewer": r.reviewer_name,
            }
            for r in p.reviews
        ],
    }


# @router.get("/search")
# def search_products(
#     category: Optional[str] = None,
#     brand: Optional[str] = None,
#     min_price: Optional[float] = None,
#     max_price: Optional[float] = None,
#     min_rating: Optional[float] = None,
#     in_stock: Optional[bool] = None,
#     limit: int = Query(20, le=100),
#     offset: int = 0,
#     db: Session = Depends(get_ecom_db),
# ):
#     query = db.query(Product).options(
#         joinedload(Product.dimensions),
#         joinedload(Product.images),
#         joinedload(Product.tags),
#         joinedload(Product.reviews),
#         joinedload(Product.meta),
#     )

#     filters = []

#     if category:
#         filters.append(Product.category == category)

#     if brand:
#         filters.append(Product.brand == brand)

#     if min_price is not None:
#         filters.append(Product.price >= min_price)

#     if max_price is not None:
#         filters.append(Product.price <= max_price)

#     if min_rating is not None:
#         filters.append(Product.rating >= min_rating)

#     if in_stock:
#         filters.append(Product.stock > 0)

#     if filters:
#         query = query.filter(and_(*filters))

#     products = query.offset(offset).limit(limit).all()

#     return [serialize_product(p) for p in products]


@router.get("/advanced-search")
def advanced_search_products(
    # -------- Product filters --------
    title: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    sku: Optional[str] = None,
    availability_status: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_discount: Optional[float] = None,
    max_discount: Optional[float] = None,
    min_rating: Optional[float] = None,
    max_rating: Optional[float] = None,
    min_stock: Optional[int] = None,
    max_stock: Optional[int] = None,
    # -------- Dimensions filters --------
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    min_height: Optional[float] = None,
    max_height: Optional[float] = None,
    min_depth: Optional[float] = None,
    max_depth: Optional[float] = None,
    # -------- Meta filters --------
    barcode: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    # -------- Review filters --------
    min_review_rating: Optional[int] = None,
    reviewer_name: Optional[str] = None,
    # -------- Tag filter --------
    tags: Optional[List[str]] = Query(None),
    # -------- Sorting --------
    sort_by: Optional[str] = "id",
    sort_order: Optional[str] = "desc",
    # -------- Pagination --------
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: Session = Depends(get_ecom_db),
):

    query = db.query(Product)

    # joins
    query = query.outerjoin(Product.dimensions)
    query = query.outerjoin(Product.meta)
    query = query.outerjoin(Product.reviews)
    query = query.outerjoin(Product.tags)

    filters = []

    # ---------- TEXT filters ----------
    if title:
        filters.append(Product.title.ilike(f"%{title}%"))

    if category:
        filters.append(Product.category == category)

    if brand:
        filters.append(Product.brand == brand)

    if sku:
        filters.append(Product.sku == sku)

    if availability_status:
        filters.append(Product.availability_status == availability_status)

    # ---------- PRICE ----------
    if min_price is not None:
        filters.append(Product.price >= min_price)

    if max_price is not None:
        filters.append(Product.price <= max_price)

    # ---------- DISCOUNT ----------
    if min_discount is not None:
        filters.append(Product.discount_percentage >= min_discount)

    if max_discount is not None:
        filters.append(Product.discount_percentage <= max_discount)

    # ---------- RATING ----------
    if min_rating is not None:
        filters.append(Product.rating >= min_rating)

    if max_rating is not None:
        filters.append(Product.rating <= max_rating)

    # ---------- STOCK ----------
    if min_stock is not None:
        filters.append(Product.stock >= min_stock)

    if max_stock is not None:
        filters.append(Product.stock <= max_stock)

    # ---------- DIMENSIONS ----------
    if min_width is not None:
        filters.append(Dimensions.width >= min_width)
    if max_width is not None:
        filters.append(Dimensions.width <= max_width)

    if min_height is not None:
        filters.append(Dimensions.height >= min_height)
    if max_height is not None:
        filters.append(Dimensions.height <= max_height)

    if min_depth is not None:
        filters.append(Dimensions.depth >= min_depth)
    if max_depth is not None:
        filters.append(Dimensions.depth <= max_depth)

    # ---------- META ----------
    if barcode:
        filters.append(Meta.barcode == barcode)

    if created_after:
        filters.append(Meta.created_at >= created_after)

    if created_before:
        filters.append(Meta.created_at <= created_before)

    # ---------- REVIEWS ----------
    if min_review_rating is not None:
        filters.append(Review.rating >= min_review_rating)

    if reviewer_name:
        filters.append(Review.reviewer_name.ilike(f"%{reviewer_name}%"))

    # ---------- TAGS ----------
    if tags:
        filters.append(ProductTag.tag.in_(tags))

    if filters:
        query = query.filter(and_(*filters))

    # ---------- GROUPING ----------
    query = query.group_by(Product.id)

    # ---------- SORTING ----------
    sort_column = getattr(Product, sort_by, Product.id)

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # ---------- PAGINATION ----------
    query = query.offset(offset).limit(limit)

    results = query.all()

    return {"count": len(results), "products": [serialize_product(p) for p in results]}
