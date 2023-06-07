from bs4 import BeautifulSoup
import requests
from srtools import cyrillic_to_latin
from models.news import NewsItem
from config import Config


class BaseScraper:
    base_url = ""
    url = ""
    institution_id = ""

    def make_params(self, page, category_id=None):
        pass

    def get_page(self, page=None, category_id=None):
        compiled_params = self.make_params(page, category_id)
        pg = requests.get(self.url, params=compiled_params)
        html = pg.text
        return html

    def parse_page(self, soup):
        raise Exception("Method not implemented")

    def parse(self, start_page=0, end_page=0, category_id=None) -> list[NewsItem]:
        """
        Some class description , sanda
        """
        news_items = []
        for i in range(start_page, end_page):
            page = self.get_page(page=i, category_id=category_id)
            soup = BeautifulSoup(page, "lxml")
            news_items += self.parse_page(soup)
            if self.parse_page == []:
                break
        return news_items


class BGFilozofski(BaseScraper):
    base_url = "https://www.f.bg.ac.rs"
    url = base_url + "/vesti"
    institution_id = 1

    def make_params(self, page, category_id=None):
        return {"IDO": category_id, "str": page}

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

    def parse_page(self, soup: BeautifulSoup) -> list[NewsItem]:
        children = soup.find_all("div", class_="vest-naslov")
        category = soup.find(id="odeljenje_vesti-naslov")
        if category:
            category = category.get_text()
        news = []
        for child in children:
            item = {}
            item["institution_id"] = self.institution_id
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
    base_url = "https://www.ff.uns.ac.rs"
    url = base_url + "/sr/vesti"
    institution_id = 2

    def make_params(self, page, category_id=None):
        return {"page": page}

    def parse_page(self, soup):
        news = []
        for element in soup.find_all("article", class_="vest-arhiva"):
            item = {}
            item["institution_id"] = self.institution_id
            title = element.find(class_="vest-naslov").get_text(strip=True)
            item["title"] = title
            date = element.find("time").get_text().replace(".", "")
            item["date"] = date
            body = element.find(class_="vest-ukratko").get_text()
            item["body"] = body
            a = element.find("a")
            href = a.attrs.get("href")
            attachment = self.base_url + href
            item["attachment"] = attachment
            news_item = NewsItem(**item)
            news.append(news_item)
        return news


