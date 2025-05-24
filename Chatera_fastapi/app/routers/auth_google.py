import os
import requests

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from .. import crud  # Assure that 'crud.py' exists in the same package
from .. import auth  # Assure that 'auth.py' exists and provides token creation functions
from app.auth import create_access_token, create_refresh_token
from app.crud import get_user_by_google_sub, create_or_update_user_google
from app.database import get_session
from app.dependencies import get_db
from app.schemas import GoogleLogin
from app.config import GOOGLE_CLIENT_ID

from sqlmodel import Session
from sqlalchemy.orm import Session

from google.auth.transport import requests as google_requests  # module Google
from google.oauth2 import id_token as google_id_token

session = get_session()




# Charger les configs
config = Config(".env")

# Config OAuth
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=config('GOOGLE_CLIENT_ID'),
    client_secret=config('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

router = APIRouter()

@router.get('/auth/google/login')
async def google_login(request: Request):
    redirect_uri = config('GOOGLE_REDIRECT_URI')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/auth/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Google authentication failed")

    user_info = await oauth.google.parse_id_token(request, token)
    

    email = user_info.get('email')
    google_sub = user_info.get('sub')  # le sub Google
    name = user_info.get('name')
    picture= user_info.get('picture')

    if not email or not google_sub:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or sub not available from Google")

    # Utilise la fonction unifiée
    user_from_db = create_or_update_user_google(db, email=email, name=name, google_sub=google_sub,picture=picture)

    access_token = auth.create_access_token(data={"sub": str(user_from_db.id)})
    refresh_token = auth.create_refresh_token(data={"sub": str(user_from_db.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/auth/google")
def login_google(google_login: GoogleLogin, db: Session = Depends(get_db)):
    try:
        # Vérifier le id_token (identité)
        idinfo = google_id_token.verify_oauth2_token(
            google_login.token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        google_sub = idinfo["sub"]
        email = idinfo.get("email")

        # **Attention**: id_token ne contient pas la photo, il faut appeler UserInfo avec access_token
        # Ici tu ne reçois que le id_token, il te faut récupérer aussi le access_token côté client !

        # Exemple : suppose que tu reçois access_token aussi dans la requête
        access_token = google_login.access_token  # Il faut modifier GoogleLogin pour ça

        # Requête UserInfo Google pour infos complètes
        userinfo_resp = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if userinfo_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch user info from Google")
        userinfo = userinfo_resp.json()
        print("GOOGLE USERINFO:", userinfo)
        name = userinfo.get("name")
        picture = userinfo.get("picture")

        user = get_user_by_google_sub(db, google_sub)
       
        user = create_or_update_user_google(
            db, email=email,name=name, google_sub=google_sub, picture=picture
        )

        # Génère token JWT local
        access_token_local = create_access_token(data={"sub": str(user.id)})
        refresh_token_local = create_refresh_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token_local,
            "refresh_token": refresh_token_local,
            "token_type": "bearer"
        }

    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")