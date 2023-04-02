from bs4 import BeautifulSoup
import requests
from models.news_model import NewsItem
from srtools import cyrillic_to_latin
from utils.db import get_db_client
from utils.exceptions import ResourceAlreadyExists

db = get_db_client()


class FilozofskiScraper:
    def list_categories(self, html):
        categories = []
        soup = BeautifulSoup(html, "lxml")
        options = soup.find_all(class_="option")
        for option in options:
            item = {}
            value = option.get("value")
            name = option.find("span")
            if value:
                id = int(option["value"].split("=")[1])
                item["id"] = id
                if name:
                    name = name.text
                    name = cyrillic_to_latin(name)
                    item["name"] = name
            categories.append(item)
        return categories

    def get_page(self, page=None, category_id=None):
        pg = requests.get(
            "https://www.f.bg.ac.rs/vesti", params={"IDO": category_id, "str": page}
        )
        txt = pg.text
        return txt

    def parse_page(self, html, category_id) -> list[NewsItem]:
        soup = BeautifulSoup(html, "lxml")
        children = soup.find_all("div", class_="vest-naslov")
        category = soup.find(id="odeljenje_vesti-naslov")
        if category:
            category = category.get_text()
        news = []
        for child in children:
            item = {}
            item["category_id"] = category_id
            item["category"] = category
            parent = child.find_parent("tr")
            if parent:
                title = parent.find(class_="vest-naslov").get_text(" ", strip=True)
                item["title"] = title
                date = parent.find(class_="vest-datum")
                date = date.get_text()
                item["date"] = date
                body = parent.find(class_="vest-telo").get_text(" ", strip=True)
                body = str(body)
                item["body"] = body
                item["attachment"] = None
                att_parent = parent.find(class_="vest-attachment")
                if att_parent:
                    a = att_parent.find("a")
                    if a:
                        href = a.attrs.get("href")
                        item["attachment"] = href
                news_item = NewsItem(**item)
                news.append(news_item)
        return news

    def count_pages(self, category_id=None):
        pg = requests.get("https://www.f.bg.ac.rs/vesti", params={"IDO": category_id})
        txt = pg.text
        tree = BeautifulSoup(txt, "lxml")
        children = tree.find_all(class_="broj-strane")
        pages = []
        for child in children:
            page = child.find("a")
            if page:
                href = page.attrs.get("href")
                href = href.split("=")[2]
                pages.append(href)
        return len(pages) + 1

    def parse(self, start_page=0, end_page=0, category_id=None) -> list[NewsItem]:
        news_items = []
        for i in range(start_page, end_page):
            page = self.get_page(page=i, category_id=category_id)
            news_items += self.parse_page(page, category_id)
            if self.parse_page == []:
                break
        return news_items

    def write_to_mongo(self, parsed_page):
        for item in parsed_page:
            item = item.dict()
            found_item = db.filozofski.find_one({"sha256_hash": item["sha256_hash"]})
            if found_item:
                raise ResourceAlreadyExists("News Item Already Exists")
            item_to_db = db.filozofski.insert_one(item)
        return item_to_db  # type: ignore


if __name__ == "__main__":
    scrappy = FilozofskiScraper()
    pass
