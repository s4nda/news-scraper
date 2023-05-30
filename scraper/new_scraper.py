from bs4 import BeautifulSoup
import requests
from srtools import cyrillic_to_latin
from models.news import NewsItem
from config import Config


class BaseScraper:
    def __init__(self, url, parameters=None):
        self.url = url
        self.parameters = parameters

    def get_page(self):
        pg = requests.get(self.url, params=self.parameters)
        html = pg.text
        return html

    def parse_page(self, html):
        soup = BeautifulSoup(html, "lxml")


class BGFilozofski(BaseScraper):
    def __init__(
        self, url, parameters=None, category_id=None, start_page=None, end_page=None
    ):
        super().__init__(url, parameters)
        self.category_id = category_id
        self.start_page = start_page
        self.end_page = end_page

    def list_categories(self):
        html = self.get_page()
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

    def parse_page(self, html, category_id) -> list[NewsItem]:
        soup = BeautifulSoup(html, "lxml")
        children = soup.find_all("div", class_="vest-naslov")
        category = soup.find(id="odeljenje_vesti-naslov")
        if category:
            category = category.get_text()
        news = []
        for child in children:
            item = {}
            item["institution_id"] = Config.filozofski_id
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


class NSFilozofski(BaseScraper):
    def __init__(self, url, parameters=None):
        super().__init__(url, parameters)
        pass


bg = BGFilozofski("https://www.f.bg.ac.rs/vesti")
ns = NSFilozofski("https://www.ff.uns.ac.rs/sr/vesti")

# scraper.get_page()

print(bg.list_categories())
