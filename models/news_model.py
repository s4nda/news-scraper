from srtools import cyrillic_to_latin
from utils.utils import month_to_int
from pydantic import BaseModel, validator, Extra
from utils.db import get_db_client
import hashlib
import datetime
import time


db = get_db_client()


class NewsItem(BaseModel):
    title: str
    body: str
    date: datetime.date
    attachment: str | None = None
    category_id: int
    category: str

    @validator("date", pre=True)
    def validate_date(cls, val):
        day, month, year = val.split("\xa0")
        month = month_to_int(month)
        d = datetime.date(int(year), month, int(day))
        return d

    @validator("title")
    def validate_title(cls, val):
        val = cyrillic_to_latin(val)
        return val

    @validator("body")
    def validate_body(cls, val):
        val = cyrillic_to_latin(val)
        return val

    @validator("category")
    def validate_category(cls, val):
        val = cyrillic_to_latin(val)
        return val

    @property
    def sha256_hash(self):
        joined_str = f"{self.title}-{self.body}"
        hashed_str = hashlib.sha256(joined_str.encode()).hexdigest()
        return hashed_str

    def dict(self):
        top = super().dict()
        top["sha256_hash"] = self.sha256_hash
        top["date"] = time.mktime(self.date.timetuple())
        return top


if __name__ == "__main__":
    pass
