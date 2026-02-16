import requests
from datetime import datetime

from src.core.ecommerce_database import EcomSessionLocal
from src.models.ecommerce_models import (
    Product,
    Dimensions,
    Review,
    ProductImage,
    ProductTag,
    Meta,
)


API_URL = "https://dummyjson.com/products?limit=100&skip={}"


def parse_date(date_str):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str.replace("Z", ""))


def fetch_all_products():
    skip = 0
    all_products = []

    while True:
        response = requests.get(API_URL.format(skip))
        data = response.json()

        products = data.get("products", [])
        all_products.extend(products)

        if len(products) == 0:
            break

        skip += 100

        if skip >= data.get("total", 0):
            break

    return all_products


def load_products():
    db = EcomSessionLocal()

    products = fetch_all_products()

    for p in products:
        existing = db.query(Product).filter(Product.id == p["id"]).first()
        if existing:
            continue

        product = Product(
            id=p["id"],
            title=p["title"],
            description=p.get("description"),
            category=p.get("category"),
            price=p.get("price"),
            discount_percentage=p.get("discountPercentage"),
            rating=p.get("rating"),
            stock=p.get("stock"),
            brand=p.get("brand"),
            sku=p.get("sku"),
            weight=p.get("weight"),
            warranty_information=p.get("warrantyInformation"),
            shipping_information=p.get("shippingInformation"),
            availability_status=p.get("availabilityStatus"),
            return_policy=p.get("returnPolicy"),
            minimum_order_quantity=p.get("minimumOrderQuantity"),
            thumbnail=p.get("thumbnail"),
        )

        db.add(product)
        db.flush()

        if "dimensions" in p:
            d = p["dimensions"]
            db.add(
                Dimensions(
                    product_id=product.id,
                    width=d.get("width"),
                    height=d.get("height"),
                    depth=d.get("depth"),
                )
            )

        for tag in p.get("tags", []):
            db.add(ProductTag(product_id=product.id, tag=tag))

        for img in p.get("images", []):
            db.add(ProductImage(product_id=product.id, url=img))

        for r in p.get("reviews", []):
            db.add(
                Review(
                    product_id=product.id,
                    rating=r.get("rating"),
                    comment=r.get("comment"),
                    date=parse_date(r.get("date")),
                    reviewer_name=r.get("reviewerName"),
                    reviewer_email=r.get("reviewerEmail"),
                )
            )

        if "meta" in p:
            m = p["meta"]
            db.add(
                Meta(
                    product_id=product.id,
                    created_at=parse_date(m.get("createdAt")),
                    updated_at=parse_date(m.get("updatedAt")),
                    barcode=m.get("barcode"),
                    qr_code=m.get("qrCode"),
                )
            )

    db.commit()
    db.close()

    print(f"Imported {len(products)} products successfully!")
