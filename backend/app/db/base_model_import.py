# Ce fichier force l'import de tous les modèles pour Alembic
# Il est utilisé uniquement dans alembic/env.py
from app.db.models.users import User
from app.models import Conversation, Message, FutureAction
