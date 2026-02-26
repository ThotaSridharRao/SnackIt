from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
import enum
import datetime
from app.core.database import Base

class RoleEnum(enum.Enum):
    customer = "customer"
    vendor = "vendor"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    preferred_language = Column(String, default="English")
    role = Column(Enum(RoleEnum), default=RoleEnum.customer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    vendor_profile = relationship("Vendor", back_populates="owner", uselist=False)
    reviews = relationship("Review", back_populates="user")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    stall_name = Column(String, index=True)
    general_location = Column(String)
    stall_image_url = Column(String, nullable=True)
    owner_image_url = Column(String, nullable=True)
    owner_details = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="vendor_profile")
    items = relationship("Item", back_populates="vendor")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float)
    image_url = Column(String, nullable=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="items")
    reviews = relationship("Review", back_populates="item")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer) # 1 to 5
    comment = Column(Text, nullable=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    item = relationship("Item", back_populates="reviews")
    user = relationship("User", back_populates="reviews")
