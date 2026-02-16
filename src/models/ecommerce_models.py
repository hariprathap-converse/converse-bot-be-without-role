from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from src.core.ecommerce_database import EcomBase


class Product(EcomBase):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    price = Column(Float)
    discount_percentage = Column(Float)
    rating = Column(Float)
    stock = Column(Integer)
    brand = Column(String(150))
    sku = Column(String(100))
    weight = Column(Float)

    warranty_information = Column(String(255))
    shipping_information = Column(String(255))
    availability_status = Column(String(100))
    return_policy = Column(String(255))
    minimum_order_quantity = Column(Integer)
    thumbnail = Column(String(500))

    dimensions = relationship("Dimensions", back_populates="product", uselist=False)
    reviews = relationship("Review", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    tags = relationship("ProductTag", back_populates="product")
    meta = relationship("Meta", back_populates="product", uselist=False)


class Dimensions(EcomBase):
    __tablename__ = "dimensions"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    width = Column(Float)
    height = Column(Float)
    depth = Column(Float)

    product = relationship("Product", back_populates="dimensions")


class Review(EcomBase):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    rating = Column(Integer)
    comment = Column(Text)
    date = Column(DateTime)
    reviewer_name = Column(String(150))
    reviewer_email = Column(String(150))

    product = relationship("Product", back_populates="reviews")


class ProductImage(EcomBase):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    url = Column(String(500))

    product = relationship("Product", back_populates="images")


class ProductTag(EcomBase):
    __tablename__ = "product_tags"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    tag = Column(String(100))

    product = relationship("Product", back_populates="tags")


class Meta(EcomBase):
    __tablename__ = "product_meta"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    barcode = Column(String(100))
    qr_code = Column(Text)

    product = relationship("Product", back_populates="meta")
