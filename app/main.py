from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, items
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="snack it! API",
    description="Backend API for the snack it! MVP (Now Powered by MongoDB)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(items.router, prefix="/items", tags=["Items"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the snack it! API"}
