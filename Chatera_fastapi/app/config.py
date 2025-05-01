# app/config.py

import os

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_URL = os.getenv("GROK_URL", "https://api.x.ai/v1/chat/completions")
