import stripe
import time

from datetime import datetime,timedelta

from pydantic_core import core_schema
from sqlalchemy import Enum


class PlanEnum(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PAYG = "payg"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.literal_schema(["free", "premium", "payg"])
    
    
def report_usage(subscription_item_id: str, quantity: int, increment=True):
    action = "increment" if increment else "set"
    try:
        usage_record = stripe.SubscriptionItem.create_usage_record(
            subscription_item=subscription_item_id,
            quantity=quantity,
            timestamp=int(time.time()),
            action=action,
        )
        return usage_record
    except Exception as e:
        print(f"Erreur lors du report d'usage Stripe : {e}")
        return None