from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core import database, security

router = APIRouter()

# --- Schemas ---
# Match the DB structure
class VendorInfo(BaseModel):
    stallName: str
    generalLocation: str
    ownerImageUrl: Optional[str] = None

class ItemBase(BaseModel):
    name: str
    description: str
    price: float
    distance: str
    imageUrl: str
    category: Optional[str] = None

class TrendingItem(ItemBase):
    id: str  # Kept as string for frontend compatibility
    rating: float
    reviewCount: int
    vendor: VendorInfo
    stallName: Optional[str] = None # For backward compatibility

class ReviewCreate(BaseModel):
    rating: int
    comment: str

class UserInfo(BaseModel):
    name: str
    email: Optional[str] = None

class ReviewOut(BaseModel):
    id: str
    item_id: str
    rating: int
    comment: str
    created_at: datetime.datetime
    user: UserInfo

# --- Endpoints ---
@router.get("/search", response_model=List[TrendingItem])
async def search_items(q: str = Query(..., min_length=1), db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Text search on name & description
    cursor = db.items.find({"$text": {"$search": q}})
    items = await cursor.to_list(length=100)
    
    result = []
    for item in items:
        # Compatibility transformations
        item_id = str(item.get("_id", item.get("id")))
        stallName = item.get("vendor", {}).get("stallName", "Unknown")
        result.append({
            **item,
            "id": item_id,
            "stallName": stallName,
        })
    return result

@router.get("/trending", response_model=List[TrendingItem])
async def get_trending_items(category: Optional[str] = None, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    query = {}
    if category and category.lower() != "all":
        # Case insensitive category match
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}
        
    cursor = db.items.find(query).sort("rating", -1).limit(20)
    items = await cursor.to_list(length=20)
    
    result = []
    for item in items:
        item_id = str(item.get("_id", item.get("id")))
        stallName = item.get("vendor", {}).get("stallName", "Unknown")
        result.append({
            **item,
            "id": item_id,
            "stallName": stallName,
        })
    return result

@router.get("/{item_id}")
async def get_item_details(item_id: str, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Check string id or ObjectId if we stored them as ObjectIds
    # For now our seed_db uses string "id" fields
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
        
    item["id"] = str(item.get("_id", item.get("id")))
    return item

@router.get("/{item_id}/reviews", response_model=List[ReviewOut])
async def get_item_reviews(item_id: str, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    cursor = db.reviews.find({"item_id": item_id}).sort("created_at", -1)
    reviews = await cursor.to_list(length=50)
    
    for r in reviews:
        r["id"] = str(r.get("_id", r.get("id")))
    return reviews


# Mock user schema since Depends(security.get_current_user) returns a dict from JWT payload
@router.post("/{item_id}/reviews")
async def add_item_review(
    item_id: str, 
    review: ReviewCreate, 
    db: AsyncIOMotorDatabase = Depends(database.get_db),
    current_user: dict = Depends(security.get_current_user) # Assuming this extracts user info
):
    # Verify item exists
    item = await db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Needs to match user shape
    user_email = current_user.get("sub")
    user_name = "Auth User" # Ideally we fetch real name from DB if not in token
    
    # Try fetching real user if we want the actual name
    db_user = await db.users.find_one({"email": user_email})
    if db_user and "name" in db_user:
        user_name = db_user["name"]
    
    new_review = {
        "item_id": item_id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": datetime.datetime.utcnow(),
        "user": {"name": user_name, "email": user_email}
    }
    
    result = await db.reviews.insert_one(new_review)
    new_review["id"] = str(result.inserted_id)
    
    # Update item's average rating & review count
    current_rating = item.get("rating", 0.0)
    current_count = item.get("reviewCount", 0)
    
    new_count = current_count + 1
    new_rating = ((current_rating * current_count) + review.rating) / new_count
    new_rating = round(new_rating, 1)
    
    await db.items.update_one(
        {"id": item_id},
        {"$set": {"rating": new_rating, "reviewCount": new_count}}
    )
    
    return {"success": True, "message": "Review added successfully", "review": new_review}

@router.get("/feed/global", response_model=List[ReviewOut])
async def get_global_feed(db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Fetch recent reviews to act as a feed
    cursor = db.reviews.find({}).sort("created_at", -1).limit(50)
    reviews = await cursor.to_list(length=50)
    
    for r in reviews:
        r["id"] = str(r.get("_id", r.get("id")))
    return reviews

# --- Vendor Specific Endpoints ---
class ItemCreate(ItemBase):
    pass

@router.get("/vendor/items")
async def get_vendor_items(db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Hardcoded for now until we have vendor auth 
    cursor = db.items.find({"vendor.stallName": "Delhi Bites"})
    vendor_items = await cursor.to_list(length=100)
    
    for item in vendor_items:
        item["id"] = str(item.get("_id", item.get("id")))
    return vendor_items

@router.post("/vendor/items")
async def add_vendor_item(item: ItemCreate, db: AsyncIOMotorDatabase = Depends(database.get_db)):
    # Mock vendor context
    import uuid
    new_id = str(uuid.uuid4())
    
    new_item = item.dict()
    new_item.update({
        "id": new_id,
        "rating": 0.0,
        "reviewCount": 0,
        "vendor": {
            "stallName": "Delhi Bites", 
            "generalLocation": "Sector 14 Market",
            "ownerImageUrl": "https://randomuser.me/api/portraits/men/32.jpg"
        },
        "created_at": datetime.datetime.utcnow()
    })
    
    result = await db.items.insert_one(new_item)
    new_item["id"] = str(result.inserted_id) # Optional: overwrite with mongo id
    return {"success": True, "item": new_item}
