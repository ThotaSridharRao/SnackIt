from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
import datetime

router = APIRouter()

# --- Mock Data ---
mock_items = {
    "1": {
        "id": "1",
        "name": "Spicy Chicken Momos",
        "description": "Authentic Tibetan style momos with a spicy garlic tomato chutney. Prepared fresh daily using hormone-free chicken.",
        "price": 4.50,
        "rating": 4.8,
        "reviewCount": 12,
        "distance": "0.8 km",
        "imageUrl": "https://images.unsplash.com/photo-1625220194771-7ebdea0b70b9?auto=format&fit=crop&w=500&q=60",
        "vendor": {
            "stallName": "Delhi Bites",
            "generalLocation": "Sector 14 Market",
            "ownerImageUrl": "https://randomuser.me/api/portraits/men/32.jpg"
        }
    },
    "2": {
        "id": "2",
        "name": "Vada Pav Classic",
        "description": "The quintessential Mumbai street food. Deep fried potato dumpling placed inside a bread bun sliced almost in half through the middle.",
        "price": 1.20,
        "rating": 4.5,
        "reviewCount": 45,
        "distance": "1.2 km",
        "imageUrl": "https://images.unsplash.com/photo-1596450514735-a1112e8e411b?auto=format&fit=crop&w=500&q=60",
        "vendor": {
            "stallName": "Mumbai Central",
            "generalLocation": "Station Road",
            "ownerImageUrl": "https://randomuser.me/api/portraits/men/44.jpg"
        }
    },
    "3": {
        "id": "3",
        "name": "Pani Puri Platter",
        "description": "Crispy hollow puri filled with a mixture of flavored water, tamarind chutney, chili, chaat masala, potato, onion or chickpeas.",
        "price": 2.00,
        "rating": 4.9,
        "reviewCount": 89,
        "distance": "2.5 km",
        "imageUrl": "https://images.unsplash.com/photo-1601050690597-df0568a70550?auto=format&fit=crop&w=500&q=60",
        "vendor": {
            "stallName": "Chaat Corner",
            "generalLocation": "Main Square",
            "ownerImageUrl": "https://randomuser.me/api/portraits/women/68.jpg"
        }
    }
}

# Mock reviews store
mock_reviews = {
    "1": [
        {"id": 101, "rating": 5, "comment": "Best momos I've ever had! So spicy and juicy.", "createdAt": "2023-10-25T10:00:00Z", "user": {"name": "John Doe"}},
        {"id": 102, "rating": 4, "comment": "Really good, but a bit too spicy for me.", "createdAt": "2023-10-26T14:30:00Z", "user": {"name": "Alice Smith"}}
    ],
    "2": [],
    "3": [
        {"id": 103, "rating": 5, "comment": "Absolutely love the tangy water!", "createdAt": "2023-11-01T09:15:00Z", "user": {"name": "Rahul Verma"}}
    ]
}

# --- Schemas ---
class TrendingItem(BaseModel):
    id: str
    name: str
    price: float
    rating: float
    stallName: str
    distance: str
    imageUrl: str

class ReviewCreate(BaseModel):
    rating: int
    comment: str

# --- Endpoints ---
@router.get("/trending", response_model=List[TrendingItem])
def get_trending_items():
    # Transform full items back to trending summary shape
    result = []
    for item_id, item in mock_items.items():
        result.append({
            "id": item["id"],
            "name": item["name"],
            "price": item["price"],
            "rating": item["rating"],
            "stallName": item["vendor"]["stallName"],
            "distance": item["distance"],
            "imageUrl": item["imageUrl"]
        })
    return result

@router.get("/{item_id}")
def get_item_details(item_id: str):
    if item_id not in mock_items:
        raise HTTPException(status_code=404, detail="Item not found")
    return mock_items[item_id]

@router.get("/{item_id}/reviews")
def get_item_reviews(item_id: str):
    if item_id not in mock_items:
        raise HTTPException(status_code=404, detail="Item not found")
    return mock_reviews.get(item_id, [])

@router.post("/{item_id}/reviews")
def add_item_review(item_id: str, review: ReviewCreate):
    if item_id not in mock_items:
        raise HTTPException(status_code=404, detail="Item not found")
    
    new_review = {
        "id": len(mock_reviews.get(item_id, [])) + 200,
        "rating": review.rating,
        "comment": review.comment,
        "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
        "user": {"name": "Current User"} # Mocking current user
    }
    
    if item_id not in mock_reviews:
        mock_reviews[item_id] = []
    
    mock_reviews[item_id].insert(0, new_review) # Add to top
    return {"success": True, "message": "Review added successfully", "review": new_review}

# --- Vendor Specific Endpoints ---

class ItemCreate(BaseModel):
    name: str
    price: float
    description: str
    imageUrl: str

@router.get("/vendor/items")
def get_vendor_items():
    # Mocking fetching just the items for the current vendor
    vendor_items = [
        item for item in mock_items.values() if item["vendor"]["stallName"] == "Delhi Bites"
    ]
    return vendor_items

@router.post("/vendor/items")
def add_vendor_item(item: ItemCreate):
    # Mock adding a new item to the store
    new_id = str(len(mock_items) + 1)
    new_item = {
        "id": new_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "rating": 0.0,
        "reviewCount": 0,
        "distance": "0.1 km",
        "imageUrl": item.imageUrl,
        "vendor": {
            "stallName": "Delhi Bites", # Assumed logged in vendor
            "generalLocation": "Sector 14 Market",
            "ownerImageUrl": "https://randomuser.me/api/portraits/men/32.jpg"
        }
    }
    
    mock_items[new_id] = new_item
    return {"success": True, "item": new_item}
