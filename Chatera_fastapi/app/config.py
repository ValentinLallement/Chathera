# app/config.py

import os
from mem0 import Memory

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_URL = os.getenv("GROK_URL", "https://api.x.ai/v1/chat/completions")

DEEPSEEK_API_KEY=os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_URL=os.getenv("DEEPSEEK_URL", "https://api.deepseek.com/chat/completions")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

config = {
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small"
        }
    },
    "vector_store": {
        "provider": "faiss",
        "config": {
            "collection_name": "conversations",
            "path": "/tmp/faiss_memories"
        }
    }
}

mem0 = Memory.from_config(config)
