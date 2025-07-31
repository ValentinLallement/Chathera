import base64
import io
import requests as external_requests  
import uuid
import random
import string
import stripe

from app.db.models import models
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse, JSONResponse

from sqlmodel import select, desc,delete,func
from sqlalchemy.ext.asyncio import AsyncSession


from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from uuid import UUID


from google.auth.transport import requests as google_requests

from app import crud, schemas, dependencies, auth
from app.db.models.models import Conversation, Bot, User, PlanEnum, SubscriptionStatus,Message,TypeEnum
from app.schemas import (
    CreateBotRequest, UserLogin, PromptRequest,
    UserDeleteRequest, ChangePasswordRequest, PasswordResetRequest, ResetPasswordRequest,EmailRequest
    ,UserSubscriptionsResponse,SubscriptionInfo,UserLegalConsentBase, UserLegalConsentRead,
    AvatarPayload,EmailSchema
)
from app.crud import get_or_create_user_consent,create_user_from_draft
from app.auth import verify_token, get_user_from_token, create_password_reset_token
from app.database import get_db
from app.dependencies import get_db
from app.config import REFRESH_SECRET_KEY, ALGORITHM, SECRET_KEY
from app.utils.permissions import check_bot_limit,MESSAGE_LIMITS
from app.utils.email import send_email_verification_code, send_email_for_password_reset,send_password_changed_email,send_account_created_email
from app.utils.payg import report_usage
from app.utils.avatar import glb_url_to_readyplayerme_headshot

from mem0 import Memory

WEBUI_API_URL = "http://127.0.0.1:7860"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


api_router = APIRouter()

@api_router.get("/")
async def read_root():
    return {"message": "Hello, FastAPI is ready!2"}

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {"status": "healthy"}

# ----------------- Register -----------------

@api_router.post("/register")
async def register_draft(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Vérif : email ou username déjà dans User
    existing_user_email = await db.execute(select(models.User).where(models.User.email == user.email))
    if existing_user_email.scalars().first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")

    existing_user_username = await db.execute(select(models.User).where(models.User.username == user.username))
    if existing_user_username.scalars().first():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur est déjà pris.")

    # 2. Vérif : email déjà dans UserDraft ? → mettre à jour le brouillon
    draft_query = await db.execute(select(models.UserDraft).where(models.UserDraft.email == user.email))
    draft = draft_query.scalars().first()

    hashed_password = await auth.hash_password(user.password)

    if draft:
        draft.username = user.username
        draft.name = user.name
        draft.password = hashed_password
    else:
        draft = models.UserDraft(
            email=user.email,
            username=user.username,
            name=user.name,
            password=hashed_password
        )
        db.add(draft)

    await db.commit()

    # 3. Supprimer les anciens codes non utilisés
    await db.execute(delete(models.EmailVerificationCode).where(
        models.EmailVerificationCode.email == user.email,
        models.EmailVerificationCode.is_used == False
    ))

    # 4. Générer un nouveau code
    code = ''.join(random.choices(string.digits, k=6))
    db_code = models.EmailVerificationCode(
        email=user.email,
        code=code,
        is_used=False,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(db_code)
    await db.commit()

    # 5. Envoyer le code
    await send_email_verification_code(user.email, code)

    return {"message": "Code envoyé. Veuillez vérifier votre email."}

@api_router.post("/resend-verification")
async def resend_verification_code(
    email_data: schemas.EmailSchema,  # simple schéma avec juste email: str
    db: AsyncSession = Depends(get_db),
):
    email = email_data.email

    # 1. Vérifier que l’email existe dans UserDraft (utilisateur en cours d’inscription)
    draft_query = await db.execute(select(models.UserDraft).where(models.UserDraft.email == email))
    draft = draft_query.scalars().first()
    if not draft:
        raise HTTPException(status_code=404, detail="Aucun brouillon d'inscription trouvé pour cet email.")

    # 2. Supprimer anciens codes non utilisés pour cet email
    await db.execute(delete(models.EmailVerificationCode).where(
        models.EmailVerificationCode.email == email,
        models.EmailVerificationCode.is_used == False
    ))

    # 3. Générer un nouveau code
    code = ''.join(random.choices(string.digits, k=6))
    db_code = models.EmailVerificationCode(
        email=email,
        code=code,
        is_used=False,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(db_code)
    await db.commit()

    # 4. Envoyer le code par mail
    await send_email_verification_code(email, code)

    return {"message": "Code de vérification renvoyé avec succès."}

@api_router.post("/verify-email-code")
async def verify_register_code(
    payload: schemas.EmailCodeVerification,
    db: AsyncSession = Depends(get_db)
):
    email = payload.email.lower().strip()

    # 1. Vérifier le code (non utilisé et valide)
    stmt_verif = (
        select(models.EmailVerificationCode)
        .where(
            (models.EmailVerificationCode.email == email) &
            (models.EmailVerificationCode.code == payload.code) &
            (models.EmailVerificationCode.is_used == False) &
            (models.EmailVerificationCode.expires_at > datetime.utcnow())
        )
    )
    result_verif = await db.execute(stmt_verif)
    code_entry = result_verif.scalars().first()

    if not code_entry:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré.")

    # 2. Marquer le code comme utilisé
    code_entry.is_used = True
    await db.commit()
    
    # 3. Créer l'utilisateur final depuis le brouillon
    user = await create_user_from_draft(db, email=email)
    

    return {"message": "Inscription confirmée", "user_id": str(user.id)}


# ----------------- Tokens -----------------

@api_router.post("/token")
async def login_for_access_token(
    user: UserLogin,
    db: AsyncSession = Depends(dependencies.get_db)
):
    user_from_db = await crud.get_user_by_username_or_email(db=db, login=user.login)
    if not user_from_db or not await auth.verify_password(user.password, user_from_db.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")

    access_token = await auth.create_access_token(data={"sub": str(user_from_db.id)})
    refresh_token = await auth.create_refresh_token(data={"sub": str(user_from_db.id)})

    response = JSONResponse(content={
        "message": "Connexion réussie",
        "access_token": access_token,
        "token_type": "bearer"
    })

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/"  # Match the proxy path
    )

    return response
    

@api_router.post("/refresh")
async def refresh_token_from_cookie(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant")

    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")

        # Convertir user_id (chaîne) en uuid.UUID
        user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id

        user = await db.get(models.User, user_uuid)
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")

        new_access_token = await auth.create_access_token(data={"sub": str(user.id)})

        return JSONResponse(content={
            "message": "Token rafraîchi avec succès",
            "access_token": new_access_token,
            "token_type": "bearer"
        })

    except JWTError:
        raise HTTPException(status_code=401, detail="Token de rafraîchissement invalide")
    
@api_router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Déconnecté"})
    response.delete_cookie(key="refresh_token")
    return response

# ----------------- User -----------------


@api_router.get("/user/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user


@api_router.delete("/user/delete")
async def delete_account(
    request: UserDeleteRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db,credentials_exception)

    # Vérifie le mot de passe
    if not await auth.verify_password(request.password, user.password):
        raise HTTPException(status_code=403, detail="Mot de passe incorrect.")

    # Supprime l'utilisateur
    db.delete(user)
    await db.commit()

    return {"detail": "Compte supprimé avec succès."}

# ----------------- Modify password -----------------

@api_router.post("/user/change-password")
async def change_password(
    request: ChangePasswordRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):  

    user = await get_user_from_token(token, db,credentials_exception)

    

    # Vérifie l'ancien mot de passe
    if not await auth.verify_password(request.old_password, user.password):
        raise HTTPException(status_code=403, detail="Ancien mot de passe incorrect.")

    # Met à jour avec le nouveau mot de passe haché
    user.password = await auth.hash_password(request.new_password)
    await db.commit()

    await send_password_changed_email(
        to_email=user.email,
        user_name=user.first_name or user.username
    )

    return {"detail": "Mot de passe mis à jour avec succès."}
# ----------------- reset password -----------------

@api_router.post("/user/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)           # Bien await ici
    user = result.scalars().first()

    # Toujours répondre pareil pour ne pas révéler l'existence de l'email
    if not user:
        return {"detail": "Si cet email existe, un lien de réinitialisation a été envoyé."}

    reset_token = await create_password_reset_token(user.id)
    reset_link = f"https://Chathera.com/reset-password?token={reset_token}"

    await send_email_for_password_reset(
        to=user.email,
        subject="Réinitialisation de votre mot de passe",
        reset_link=reset_link
    )

    return {"detail": "Si cet email existe, un lien de réinitialisation a été envoyé."}


@api_router.post("/user/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")

    # On retire le int() car user_id est un UUID en string
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    user.password = await auth.hash_password(request.new_password)
    db.add(user)
    await db.commit()

    await send_password_changed_email(
        to_email=user.email,
        user_name=user.name or user.username
    )

    return {"detail": "Mot de passe réinitialisé avec succès."}

# ----------------- Images -----------------



@api_router.post("/generate-image/")
async def generate_image(data: PromptRequest, token: str = Depends(verify_token)):
    """
    Génère une image protégée par token via l'API Stable Diffusion Web-UI.
    """
    payload = {
        "prompt": data.prompt,
        "steps": 30,
        "sampler_index": "Euler a",
        "cfg_scale": 7.5,
        "width": 512,
        "height": 512,
    }

    try:
        response = external_requests.post(f"{WEBUI_API_URL}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
        r = response.json()
        image_data = base64.b64decode(r['images'][0])
        return StreamingResponse(io.BytesIO(image_data), media_type="image/png")

    except external_requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erreur API Web-UI : {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
    

# ----------------- Bots -----------------


@api_router.post("/create_bot")
async def create_bot_and_conversation(
    request: CreateBotRequest,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Impossible de valider les identifiants.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Récupération utilisateur via token
    user = await get_user_from_token(token, db, credentials_exception)

    # Vérifie que l'utilisateur a un abonnement
    result = await db.execute(
        select(models.Subscription).where(models.Subscription.user_id == user.id)
    )
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé pour l'utilisateur")

    # Si plan ≠ FREE, abonnement doit être actif
    if subscription.plan != PlanEnum.FREE and subscription.status != SubscriptionStatus.active:
        raise HTTPException(
            status_code=403,
            detail="Votre abonnement n'est pas actif. Merci de le réactiver pour utiliser le service."
        )

    # Compter les bots existants
    result = await db.execute(
        select(models.Bot).where(models.Bot.user_id == user.id)
    )
    existing_bots = result.scalars().all()
    existing_bot_count = len(existing_bots)

    # Vérifier la limite
    if not await check_bot_limit(subscription, existing_bot_count):
        raise HTTPException(status_code=403, detail="Limite de bots atteinte pour votre abonnement")

    if subscription.plan == PlanEnum.FREE:
        bot_type = TypeEnum.free
    elif subscription.plan == PlanEnum.PREMIUM:
        bot_type = TypeEnum.premium
    elif subscription.plan == PlanEnum.PAYG:
        bot_type = TypeEnum.payg
    else:
        bot_type = TypeEnum.free  # fallback de sécurité

    # Création du bot et conversation
    try:
        new_bot = models.Bot(
            name=request.name,
            user_id=user.id,
            gender=request.gender,
            personality=request.personality,
            type=bot_type
        )
        db.add(new_bot)
        await db.commit()
        await db.refresh(new_bot)

        new_conversation = models.Conversation(
            user_id=user.id,
            bot_id=new_bot.id
        )
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)

        # Report d’usage Stripe (facultatif)
        if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_bots:
            try:
                report_usage(
                    subscription_item_id=subscription.stripe_subscription_item_bots,
                    quantity=1,
                    increment=True
                )
            except Exception as e:
                print(f"Erreur lors du report d'usage bots à Stripe : {e}")

        return {
            "bot_id": new_bot.id,
            "conversation_id": new_conversation.id
        }

    except Exception as e:
        await db.rollback()
        print(f"Erreur serveur lors de la création du bot : {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur lors de la création du bot.")


@api_router.delete("/delete_bot/{bot_id}")
async def delete_bot(
    bot_id: UUID,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Attention à await db.execute et récupérer le résultat avant .scalars().first()
    stmt_bot = select(Bot).where(Bot.id == bot_id, Bot.user_id == user.id)
    result_bot = await db.execute(stmt_bot)
    bot = result_bot.scalars().first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot non trouvé ou pas les droits")

    stmt_sub = select(models.Subscription).where(models.Subscription.user_id == user.id)
    result_sub = await db.execute(stmt_sub)
    subscription = result_sub.scalars().first()
    if not subscription:
        raise HTTPException(status_code=403, detail="Aucun abonnement trouvé")

    try:
        # Supprimer les conversations liées
        stmt_conv = select(Conversation).where(Conversation.bot_id == bot.id)
        result_conv = await db.execute(stmt_conv)
        conversations = result_conv.scalars().all()

        for conv in conversations:
            await db.delete(conv)  # La méthode delete() est asynchrone en AsyncSession

        await db.commit()

        await db.delete(bot)
        await db.commit()

        if subscription.plan == PlanEnum.PAYG and subscription.stripe_subscription_item_bots:
            try:
                report_usage(subscription_item_id=subscription.stripe_subscription_item_bots, quantity=1, increment=False)
            except Exception as e:
                print(f"Erreur report Stripe suppression bot : {e}")

        return {"detail": f"Bot {bot.name} supprimé avec succès"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression : {e}")


@api_router.get("/my_bots")
async def get_my_bots(token: str = Depends(dependencies.oauth2_scheme), db: AsyncSession = Depends(dependencies.get_db)):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Récupérer tous les bots de l'utilisateur
    stmt_bots = select(Bot).where(Bot.user_id == user.id)
    result = await db.execute(stmt_bots)
    bots = result.scalars().all()

    bots_with_last_message = []

    for bot in bots:
        # Récupérer la conversation unique user-bot
        stmt_conv = select(Conversation).where(
            Conversation.user_id == user.id,
            Conversation.bot_id == bot.id
        )
        conv_result = await db.execute(stmt_conv)
        conversation = conv_result.scalars().first()

        last_message_info = None

        if conversation:
            # Récupérer le dernier message par date décroissante
            stmt_last_msg = (
                select(Message)
                .where(Message.conversation_id == conversation.id)
                .order_by(desc(Message.created_at))
                .limit(1)
            )
            msg_result = await db.execute(stmt_last_msg)
            last_message = msg_result.scalars().first()

            if last_message:
                # Identifier l'expéditeur : user ou bot
                # On suppose que si last_message.user_id == user.id => "user"
                # sinon => "bot" (car le bot n'a pas user_id défini ou différent)
                sender = "user" if last_message.user_id == user.id else "bot"

                last_message_info = {
                    "content": last_message.content,
                    "sender": sender,
                    "created_at": last_message.created_at.isoformat(),
                }

        bots_with_last_message.append({
            "bot_id": str(bot.id),
            "name": bot.name,
            "gender": bot.gender if bot.gender else None,
            "avatar_url": bot.avatar_url,
            "url": bot.url,
            "type":bot.type,
            "last_message": last_message_info,
        })

    return bots_with_last_message


@api_router.post("/save-avatar")
async def save_avatar(
    payload: AvatarPayload,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    # Authentification de l'utilisateur via token
    credentials_exception = HTTPException(status_code=401, detail="Token invalide")
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Recherche du bot
    result = await db.execute(select(models.Bot).where(models.Bot.id == payload.bot_id))
    bot = result.scalars().first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot introuvable")

    # Vérification des droits d'accès au bot
    if bot.user_id != user.id:
        raise HTTPException(status_code=403, detail="Accès interdit : ce bot ne vous appartient pas")

    # Conversion GLB vers PNG
    try:
        png_url = glb_url_to_readyplayerme_headshot(payload.glb_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Sauvegarde de l'avatar
    bot.avatar_url = png_url
    bot.url = payload.glb_url
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Avatar enregistré avec succès",
            "bot_id": str(bot.id),
            "avatar_url": bot.avatar_url,
        },
    )

# ----------------- Abonnements -----------------

@api_router.put("/user/subscription/update", response_model=schemas.SubscriptionUpdate)
async def update_my_subscription(
    subscription_update: schemas.SubscriptionUpdate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = subscription_update.dict(exclude_unset=True)

    try:
        updated_subscription = await crud.update_user_subscription(
            db=db,
            user_id=user.id,
            new_plan=update_data.get("plan"),
            message_limit=update_data.get("message_limit"),
            message_limit_provided="message_limit" in update_data
        )
        return updated_subscription
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    

@api_router.get("/user/subscription/infos", response_model=UserSubscriptionsResponse)
async def get_user_subscription(
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt_sub = select(models.Subscription).where(models.Subscription.user_id == user.id)
    result = await db.execute(stmt_sub)
    subscription = result.scalars().first()

    if not subscription:
        return UserSubscriptionsResponse(subscriptions=None)

    # Compter les bots de l'utilisateur
    stmt_bot_count = select(func.count()).select_from(models.Bot).where(models.Bot.user_id == user.id)
    bot_count_result = await db.execute(stmt_bot_count)
    bot_count = bot_count_result.scalar_one()

    # Calcul du message_limit en fonction du plan
    plan = subscription.plan
    message_limit = MESSAGE_LIMITS.get(plan)

    if plan == PlanEnum.PAYG:
        # Pour PAYG, on utilise le message_limit de l'abonnement s'il est défini
        if subscription.message_limit is not None:
            message_limit = subscription.message_limit
        else:
            message_limit = MESSAGE_LIMITS.get(PlanEnum.PAYG)

    # Création de l’objet de base
    subs_info = SubscriptionInfo(
        id=subscription.id,
        user_id=user.id,
        plan=plan,
        status=subscription.status,
        message_count=subscription.message_count,
        free_message_count=subscription.free_message_count,
        message_limit=message_limit,
        bot_count=bot_count,
    )

    # 🔁 Ajout des données Stripe si nécessaire
    if subscription.stripe_subscription_id:
        try:
            stripe_sub = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id,
                expand=["items.data.price"]
            )

            item = stripe_sub["items"]["data"][0] if stripe_sub.get("items") and stripe_sub["items"]["data"] else None

            if item:
                subs_info.stripe_current_period_start = datetime.fromtimestamp(
                    item.get("current_period_start")) if item.get("current_period_start") else None
                subs_info.stripe_current_period_end = datetime.fromtimestamp(
                    item.get("current_period_end")) if item.get("current_period_end") else None

            subs_info.stripe_cancel_at_period_end = stripe_sub.get("cancel_at_period_end")

            price = item.get("price", {}) if item else {}
            subs_info.stripe_plan_amount_eur = (price.get("unit_amount", 0) / 100) if price.get("unit_amount") else None
            subs_info.stripe_currency = price.get("currency")

        except Exception as e:
            print(f"[SubscriptionInfo] Erreur Stripe : {e}")

    # ➕ Ajout dynamique du champ remaining (non défini dans SubscriptionInfo)
    remaining = None
    if message_limit is not None:
        remaining = max(0, message_limit - subscription.message_count)

    # Retourne l'objet enrichi via un dict
    return {
        "subscriptions": {
            **subs_info.dict(),
            "remaining": remaining
        }
    }

# ------------------------- Consent -------------------------

@api_router.post("/legal/accept", response_model=UserLegalConsentRead)
async def accept_legal_consent(
    consent_data: UserLegalConsentBase,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    consent = await get_or_create_user_consent(db, user.id)

    now = datetime.now(timezone.utc)
    # Pour chaque champ accepté à True, on met à jour la date correspondante
    if consent_data.accepted_terms is True:
        consent.accepted_terms = True
        consent.accepted_terms_at = now

    if consent_data.accepted_privacy is True:
        consent.accepted_privacy = True
        consent.accepted_privacy_at = now

    if consent_data.accepted_cookies is True:
        consent.accepted_cookies = True
        consent.accepted_cookies_at = now

    await db.commit()
    await db.refresh(consent)
    return consent


@api_router.put("/legal/update", response_model=UserLegalConsentRead)
async def update_legal_consent(
    update_data: UserLegalConsentBase,
    token: str = Depends(dependencies.oauth2_scheme),
    db: AsyncSession = Depends(dependencies.get_db)
):
    user = await get_user_from_token(token, db, credentials_exception)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    consent = await get_or_create_user_consent(db, user.id)
    now = datetime.now(timezone.utc)

    # Modifie chaque champ, met à jour la date ou supprime la date si False
    if update_data.accepted_terms is not None:
        consent.accepted_terms = update_data.accepted_terms
        consent.accepted_terms_at = now if update_data.accepted_terms else None

    if update_data.accepted_privacy is not None:
        consent.accepted_privacy = update_data.accepted_privacy
        consent.accepted_privacy_at = now if update_data.accepted_privacy else None

    if update_data.accepted_cookies is not None:
        consent.accepted_cookies = update_data.accepted_cookies
        consent.accepted_cookies_at = now if update_data.accepted_cookies else None

    await db.commit()
    await db.refresh(consent)
    return consent
