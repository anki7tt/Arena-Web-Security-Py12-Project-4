import os
import unittest
from bs4 import BeautifulSoup
from database import ProductDatabase
from scraper import BookScraper

class TestProductMarketResearch(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_run.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = ProductDatabase(self.test_db_path)

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        if os.path.exists("test_export.csv"):
            os.remove("test_export.csv")

    def test_database_crud(self):
        pid = self.db.insert_product("Test Book", 19.99, "In stock", "http://example.com/test-book")
        self.assertIsNotNone(pid)

        item = self.db.get_product_by_id(pid)
        self.assertIsNotNone(item)
        self.assertEqual(item["title"], "Test Book")
        self.assertEqual(item["price"], 19.99)
        self.assertEqual(item["availability"], "In stock")

        updated = self.db.update_product(pid, price=24.50, availability="Out of stock")
        self.assertTrue(updated)
        item_updated = self.db.get_product_by_id(pid)
        self.assertEqual(item_updated["price"], 24.50)
        self.assertEqual(item_updated["availability"], "Out of stock")

        deleted = self.db.delete_product(pid)
        self.assertTrue(deleted)
        self.assertIsNone(self.db.get_product_by_id(pid))

    def test_duplicate_prevention(self):
        pid1 = self.db.insert_product("Duplicate Book", 15.00, "In stock", "http://example.com/dup")
        self.assertIsNotNone(pid1)

        pid2 = self.db.insert_product("Duplicate Book 2", 20.00, "In stock", "http://example.com/dup")
        self.assertIsNone(pid2)
        self.assertEqual(self.db.get_total_count(), 1)

    def test_analytics_and_search(self):
        items = [
            {"title": "Python Basics", "price": 10.0, "availability": "In stock", "product_url": "http://example.com/1"},
            {"title": "Advanced Python", "price": 30.0, "availability": "In stock", "product_url": "http://example.com/2"},
            {"title": "Data Science", "price": 20.0, "availability": "In stock", "product_url": "http://example.com/3"},
        ]
        self.db.insert_many(items)

        self.assertEqual(self.db.get_total_count(), 3)
        self.assertEqual(self.db.get_average_price(), 20.0)

        cheapest, expensive = self.db.get_price_extremes()
        self.assertEqual(cheapest["price"], 10.0)
        self.assertEqual(expensive["price"], 30.0)

        results = self.db.search_products(query="python")
        self.assertEqual(len(results), 2)

        price_filtered = self.db.search_products(min_price=15.0, max_price=25.0)
        self.assertEqual(len(price_filtered), 1)
        self.assertEqual(price_filtered[0]["title"], "Data Science")

    def test_csv_export(self):
        self.db.insert_product("Export Book", 12.00, "In stock", "http://example.com/exp")
        count = self.db.export_to_csv("test_export.csv")
        self.assertEqual(count, 1)
        self.assertTrue(os.path.exists("test_export.csv"))

    def test_scraper_pod_parser(self):
        html = """
        <article class="product_pod">
            <div class="image_container"></div>
            <h3><a href="sample_100/index.html" title="Sample Book Title">Sample Book Title</a></h3>
            <div class="product_price">
                <p class="price_color">£45.50</p>
                <p class="instock availability"><i class="icon-ok"></i> In stock</p>
            </div>
        </article>
        """
        soup = BeautifulSoup(html, "html.parser")
        pod = soup.find("article", class_="product_pod")
        scraper = BookScraper()
        item = scraper.parse_product_pod(pod, "http://books.toscrape.com/catalogue/page-1.html")

        self.assertIsNotNone(item)
        self.assertEqual(item["title"], "Sample Book Title")
        self.assertEqual(item["price"], 45.50)
        self.assertIn("In stock", item["availability"])
        self.assertEqual(item["product_url"], "http://books.toscrape.com/catalogue/sample_100/index.html")

if __name__ == "__main__":
    unittest.main()
