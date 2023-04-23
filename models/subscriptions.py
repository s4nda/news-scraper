from pydantic import BaseModel, Field
from utils.db import get_db_client
import uuid
import time

db = get_db_client()


class UserSubscriptions(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    institution_id: int
    category_id: int
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class SubsModel:
    def create(self, subscription: UserSubscriptions) -> UserSubscriptions:
        sub_dict = subscription.dict()
        db.subs.insert_one(sub_dict)
        created = db.subs.find_one({"id": subscription.id})
        return UserSubscriptions.parse_obj(created)

    def delete(self, subscription: UserSubscriptions) -> None:
        db.subs.delete_one({"id": subscription.id})
