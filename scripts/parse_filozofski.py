from scraper.filozofski_scraper import FilozofskiScraper
from utils.db import get_db_client
from utils.logger import log

if __name__ == "__main__":
    db = get_db_client()
    scrappy = FilozofskiScraper()
    categories = [cat["id"] for cat in db.categories.find()]
    for i in categories:
        try:
            news = scrappy.parse(start_page=0, end_page=2, category_id=i)
        except Exception as e:
            log.error(
                f"An error occurred while parsing news for category {i}", exc_info=True
            )
            continue
        fresh_news = []
        for item in news:
            try:
                item = item.dict()
                found_item = db.filozofski.find_one(
                    {"sha256_hash": item["sha256_hash"]}
                )
                if found_item:
                    continue
                db.filozofski.insert_one(item)
                fresh_news.append(item)
            except Exception as e:
                log.error(
                    f"An error occurred while inserting news item for category {i}",
                    exc_info=True,
                )
        if len(fresh_news):
            found_subs = db.subs.find({"category_id": i, "institution_id": 1})
            subscribers = []
            for sub in found_subs:
                found_user = db.users.find_one({"id": sub["user_id"]})
                subscribers.append(found_user)
            for user in subscribers:
                log.info(f"sending email to: {user['email']}")
        log.info(f"Novih vesti: {len(fresh_news)}")


