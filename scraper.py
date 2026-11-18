import re
import time
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class BookScraper:
    def __init__(self, base_url="http://books.toscrape.com/", delay=0.8):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })

    def fetch_page(self, page_number):
        url = urljoin(self.base_url, f"catalogue/page-{page_number}.html")
        try:
            response = self.session.get(url, timeout=12)
            if response.status_code == 200:
                return response.text, url
            return None, url
        except requests.RequestException:
            return None, url

    def parse_product_pod(self, pod, current_url):
        try:
            link_tag = pod.find("h3").find("a")
            title = link_tag.get("title") or link_tag.text.strip()
            relative_url = link_tag.get("href")
            product_url = urljoin(current_url, relative_url)

            price_tag = pod.find("p", class_="price_color")
            price_text = price_tag.text if price_tag else "0.0"
            match = re.search(r"[\d.]+", price_text)
            price = float(match.group()) if match else 0.0

            avail_tag = pod.find("p", class_="instock")
            availability = avail_tag.text.strip() if avail_tag else "Unknown"

            return {
                "title": title,
                "price": price,
                "availability": availability,
                "product_url": product_url
            }
        except (AttributeError, ValueError):
            return None

    def scrape(self, target_count=35, max_pages=5):
        collected = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            html, current_url = self.fetch_page(page)
            if not html:
                break

            soup = BeautifulSoup(html, "html.parser")
            pods = soup.find_all("article", class_="product_pod")
            if not pods:
                break

            for pod in pods:
                item = self.parse_product_pod(pod, current_url)
                if item and item["product_url"] not in seen_urls:
                    seen_urls.add(item["product_url"])
                    collected.append(item)
                    if len(collected) >= target_count:
                        return collected

            time.sleep(self.delay)

        return collected
