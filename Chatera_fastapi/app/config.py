# app/config.py

import os

from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_URL = os.getenv("GROK_URL", "https://api.x.ai/v1/chat/completions")

DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL=os.getenv("DEEPSEEK_URL", "https://api.deepseek.com/chat/completions")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))  

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")    
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

PREMIUM_PRICE_ID = os.getenv("PREMIUM_PRICE_ID")
PAYG_PRICE_ID = os.getenv("PAYG_PRICE_ID")

MESSAGE_PRICE_ID= os.getenv("MESSAGE_PRICE_ID") 
BOT_PRICE_ID = os.getenv("BOT_PRICE_ID")  


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Configuration mem0 
config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-large"
        }
    },
    "vector_store": {
        "provider": "faiss",
        "config": {
            "collection_name": "conversations",
            "path": "C:\\Users\\lalle\\projets\\Chathera\\Chatera_fastapi\\faiss_memories"
        }
    }
}