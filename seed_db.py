import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

async def seed_db():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["sfd_db"]
    
    # Check if collections exist and clear them
    print("Clearing existing items and reviews...")
    await db.items.delete_many({})
    await db.reviews.delete_many({})

    mock_items = [
        {
            "id": "1", # Keeping string ID for backward compatibility with frontend
            "name": "Spicy Chicken Momos",
            "description": "Authentic Tibetan style momos with a spicy garlic tomato chutney. Prepared fresh daily using hormone-free chicken.",
            "price": 4.50,
            "rating": 4.8,
            "reviewCount": 2,
            "distance": "0.8 km",
            "imageUrl": "https://images.unsplash.com/photo-1625220194771-7ebdea0b70b9?auto=format&fit=crop&w=500&q=60",
            "vendor": {
                "stallName": "Delhi Bites",
                "generalLocation": "Sector 14 Market",
                "ownerImageUrl": "https://randomuser.me/api/portraits/men/32.jpg"
            },
            "category": "Snacks",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "id": "2",
            "name": "Vada Pav Classic",
            "description": "The quintessential Mumbai street food. Deep fried potato dumpling placed inside a bread bun sliced almost in half through the middle.",
            "price": 1.20,
            "rating": 4.5,
            "reviewCount": 0,
            "distance": "1.2 km",
            "imageUrl": "https://images.unsplash.com/photo-1596450514735-a1112e8e411b?auto=format&fit=crop&w=500&q=60",
            "vendor": {
                "stallName": "Mumbai Central",
                "generalLocation": "Station Road",
                "ownerImageUrl": "https://randomuser.me/api/portraits/men/44.jpg"
            },
            "category": "Snacks",
            "created_at": datetime.datetime.utcnow()
        },
        {
            "id": "3",
            "name": "Pani Puri Platter",
            "description": "Crispy hollow puri filled with a mixture of flavored water, tamarind chutney, chili, chaat masala, potato, onion or chickpeas.",
            "price": 2.00,
            "rating": 4.9,
            "reviewCount": 1,
            "distance": "2.5 km",
            "imageUrl": "https://images.unsplash.com/photo-1601050690597-df0568a70550?auto=format&fit=crop&w=500&q=60",
            "vendor": {
                "stallName": "Chaat Corner",
                "generalLocation": "Main Square",
                "ownerImageUrl": "https://randomuser.me/api/portraits/women/68.jpg"
            },
            "category": "Chaat",
            "created_at": datetime.datetime.utcnow()
        }
    ]

    print("Inserting mock items...")
    await db.items.insert_many(mock_items)

    mock_reviews = [
        {
            "id": "101",
            "item_id": "1",
            "rating": 5,
            "comment": "Best momos I've ever had! So spicy and juicy.",
            "created_at": datetime.datetime.utcnow(),
            "user": {"name": "John Doe", "email": "john@example.com"}
        },
        {
            "id": "102",
            "item_id": "1",
            "rating": 4,
            "comment": "Really good, but a bit too spicy for me.",
            "created_at": datetime.datetime.utcnow(),
            "user": {"name": "Alice Smith", "email": "alice@example.com"}
        },
        {
            "id": "103",
            "item_id": "3",
            "rating": 5,
            "comment": "Absolutely love the tangy water!",
            "created_at": datetime.datetime.utcnow(),
            "user": {"name": "Rahul Verma", "email": "rahul@example.com"}
        }
    ]

    print("Inserting mock reviews...")
    await db.reviews.insert_many(mock_reviews)

    # Need a text index on items for search
    print("Creating text indices...")
    await db.items.create_index([("name", "text"), ("description", "text")])

    print("Database seeding completed successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_db())
