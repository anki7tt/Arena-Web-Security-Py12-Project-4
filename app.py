import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from database import ProductDatabase
from scraper import BookScraper

app = Flask(__name__)
app.secret_key = "super_market_research_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "products.db")
db = ProductDatabase(DB_PATH)

@app.route("/")
def index():
    query = request.args.get("query", "").strip()
    min_price_raw = request.args.get("min_price", "").strip()
    max_price_raw = request.args.get("max_price", "").strip()

    min_price = float(min_price_raw) if min_price_raw else None
    max_price = float(max_price_raw) if max_price_raw else None

    if query or min_price is not None or max_price is not None:
        products = db.search_products(query=query, min_price=min_price, max_price=max_price)
    else:
        products = db.get_all_products()

    total_count = db.get_total_count()
    average_price = db.get_average_price()
    cheapest, expensive = db.get_price_extremes()

    return render_template(
        "index.html",
        products=products,
        total_count=total_count,
        average_price=average_price,
        cheapest=cheapest,
        expensive=expensive,
        query=query,
        min_price=min_price_raw,
        max_price=max_price_raw
    )

@app.route("/scrape-now", methods=["POST"])
def scrape_now():
    scraper = BookScraper(delay=0.5)
    records = scraper.scrape(target_count=40)
    if records:
        inserted, skipped = db.insert_many(records)
        flash(f"Scraped {len(records)} products. Added {inserted} new, skipped {skipped} duplicates.", "success")
    else:
        flash("Failed to scrape records from the target website.", "danger")
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add_product():
    title = request.form.get("title", "").strip()
    price_val = request.form.get("price", "0").strip()
    availability = request.form.get("availability", "In stock").strip()
    product_url = request.form.get("product_url", "").strip()

    try:
        price = float(price_val)
        result = db.insert_product(title, price, availability, product_url)
        if result:
            flash(f"Product '{title}' added successfully.", "success")
        else:
            flash("Could not add product. It might be a duplicate URL.", "warning")
    except ValueError:
        flash("Invalid price value provided.", "danger")

    return redirect(url_for("index"))

@app.route("/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    if db.delete_product(product_id):
        flash("Product deleted successfully.", "info")
    else:
        flash("Failed to delete product.", "danger")
    return redirect(url_for("index"))

@app.route("/export")
def export_csv():
    export_path = os.path.join(BASE_DIR, "products_export.csv")
    count = db.export_to_csv(export_path)
    if count == 0:
        flash("No products available to export.", "warning")
        return redirect(url_for("index"))
    return send_file(export_path, as_attachment=True, download_name="market_research_products.csv")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
