import asyncio
import warnings
from dotenv import load_dotenv
import os

load_dotenv()

PRODUCTION = True if os.getenv("PRODUCTION") == "True" else False

# ignore les avertissements de dépréciation venus de FAISS
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module="faiss.loader"
)

# ignore les messages du type "builtin type SwigPyPacked has no __module__"
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=r"builtin type .* has no __module__"
)


warnings.filterwarnings("ignore", category=DeprecationWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from starlette.middleware.sessions import SessionMiddleware

from contextlib import asynccontextmanager

from app.websocket.router import websocket_router
from app.routers import message,auth_google,stripe_routes,api_routers
from app.tasks.scheduler import task_scheduler
from app.routers.api_routers import api_router


# --- lifespan ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler_task = asyncio.create_task(task_scheduler())
    yield
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

# --- création unique de l'app avec lifespan ---
app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="une_clef_secrete_pour_session")

if PRODUCTION: 
    print("Production mode: CORS configured for production origin")
    origins = [
        "https://chathera.com",  # front-end origin
    ]
    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://chathera.com"],  # Explicitly allow the frontend origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    origins = [
        "http://localhost:5173",  # front-end origin
    ]
    # CORS middleware configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Explicitly allow the frontend origin
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )



# API routes
app.include_router(websocket_router)
app.include_router(message.router,prefix="/api")
app.include_router(auth_google.router)
app.include_router(stripe_routes.router, prefix="/api" )
app.include_router(api_router, prefix="/api")



######################
#        Front       #
######################


"""# Serve static files from frontend build 
app.mount("/static", StaticFiles(directory="../frontend/dist/static"), name="static")

BASE_DIR = Path(__file__).parent
favicon_path = BASE_DIR / 'favicon.webp'

@app.get('/favicon.webp', include_in_schema=False)
async def favicon():
    return FileResponse(str(favicon_path))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse("../frontend/dist/index.html")

"""


