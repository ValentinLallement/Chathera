from datetime import datetime,timedelta
from sqlalchemy.orm import Session

from pydantic_core import core_schema
from sqlalchemy import Enum

class PlanEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PAYG = "payg"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.literal_schema(["free", "premium", "payg"])
    
    
# exemple de fonction qui calcule l'utilisation mensuelle des utilisateurs - A modifier pour adapter à Stripe ! 
def compute_monthly_usage(db: Session):
    from app.models import User, UsageLog, MonthlyUsage
    now = datetime.utcnow()
    first_day_last_month = datetime(now.year, now.month, 1) - timedelta(days=1)
    start = datetime(first_day_last_month.year, first_day_last_month.month, 1)
    end = datetime(now.year, now.month, 1)

    users = db.query(User).all()
    for user in users:
        logs = db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= start,
            UsageLog.timestamp < end
        ).all()

        msg_count = sum(1 for log in logs if log.type == "message")
        bot_count = sum(1 for log in logs if log.type == "bot_creation")

        usage = MonthlyUsage(
            user_id=user.id,
            year=start.year,
            month=start.month,
            total_messages=msg_count,
            total_bots_created=bot_count,
            billed=False
        )
        db.add(usage)

    db.commit()