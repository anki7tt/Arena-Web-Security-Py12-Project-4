import os
import sys
from database import ProductDatabase
from scraper import BookScraper

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(title):
    print("=" * 65)
    print(f" {title.upper()} ".center(65, "="))
    print("=" * 65)

def format_product_row(product):
    return f"[{product['id']:3d}] £{product['price']:6.2f} | {product['availability']:<12} | {product['title'][:42]}"

def display_product_list(products):
    if not products:
        print("\nNo products found.")
        return
    print("\n" + "-" * 75)
    print(f"{'ID':<6} {'PRICE':<9} {'STATUS':<15} {'TITLE'}")
    print("-" * 75)
    for p in products:
        print(f"{p['id']:<6} £{p['price']:<8.2f} {p['availability']:<15} {p['title']}")
    print("-" * 75)
    print(f"Total shown: {len(products)}")

def handle_scrape(db):
    print_header("Web Scraping: Books to Scrape")
    print("Target website: http://books.toscrape.com/")
    print("Collecting at least 35 product records...")
    scraper = BookScraper(delay=0.6)
    records = scraper.scrape(target_count=35)
    if not records:
        print("Failed to fetch product records. Check internet connection.")
        return

    inserted, skipped = db.insert_many(records)
    print(f"\nScraping finished successfully!")
    print(f"Total fetched: {len(records)}")
    print(f"New records inserted: {inserted}")
    print(f"Duplicates skipped:    {skipped}")

def handle_view_all(db):
    print_header("Product Catalog")
    products = db.get_all_products()
    display_product_list(products)

def handle_search_filter(db):
    print_header("Search and Filter Products")
    query = input("Enter search keyword in title (leave blank for any): ").strip()
    min_price_in = input("Enter minimum price (leave blank for any): ").strip()
    max_price_in = input("Enter maximum price (leave blank for any): ").strip()

    min_price = float(min_price_in) if min_price_in else None
    max_price = float(max_price_in) if max_price_in else None

    results = db.search_products(query=query if query else None, min_price=min_price, max_price=max_price)
    display_product_list(results)

def handle_price_extremes(db):
    print_header("Cheapest & Most Expensive Products")
    cheapest, expensive = db.get_price_extremes()
    if not cheapest or not expensive:
        print("No products available in the database.")
        return

    print("\n[CHEAPEST PRODUCT]")
    print(f"  ID:           {cheapest['id']}")
    print(f"  Title:        {cheapest['title']}")
    print(f"  Price:        £{cheapest['price']:.2f}")
    print(f"  Availability: {cheapest['availability']}")
    print(f"  URL:          {cheapest['product_url']}")

    print("\n[MOST EXPENSIVE PRODUCT]")
    print(f"  ID:           {expensive['id']}")
    print(f"  Title:        {expensive['title']}")
    print(f"  Price:        £{expensive['price']:.2f}")
    print(f"  Availability: {expensive['availability']}")
    print(f"  URL:          {expensive['product_url']}")

def handle_statistics(db):
    print_header("Market Research Statistics")
    total = db.get_total_count()
    avg_price = db.get_average_price()
    cheapest, expensive = db.get_price_extremes()

    print(f"\nTotal Products Stored: {total}")
    print(f"Average Product Price: £{avg_price:.2f}")
    if cheapest and expensive:
        print(f"Price Range:           £{cheapest['price']:.2f} - £{expensive['price']:.2f}")
        price_spread = expensive['price'] - cheapest['price']
        print(f"Price Spread:          £{price_spread:.2f}")

def handle_manual_insert(db):
    print_header("Add Product Manually")
    title = input("Product title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return

    price_str = input("Price: ").strip()
    try:
        price = float(price_str)
    except ValueError:
        print("Invalid price value.")
        return

    availability = input("Availability (e.g., In stock / Out of stock) [In stock]: ").strip()
    if not availability:
        availability = "In stock"

    product_url = input("Product URL: ").strip()
    if not product_url:
        print("Product URL cannot be empty.")
        return

    result = db.insert_product(title, price, availability, product_url)
    if result:
        print(f"\nProduct inserted successfully with ID {result}.")
    else:
        print("\nFailed to insert. A product with this URL already exists.")

def handle_update(db):
    print_header("Update Product Record")
    id_str = input("Enter Product ID to update: ").strip()
    if not id_str.isdigit():
        print("Invalid ID.")
        return

    product_id = int(id_str)
    existing = db.get_product_by_id(product_id)
    if not existing:
        print(f"No product found with ID {product_id}.")
        return

    print(f"\nCurrent Title: {existing['title']}")
    new_title = input("New Title (leave blank to keep current): ").strip()

    print(f"Current Price: £{existing['price']:.2f}")
    new_price_str = input("New Price (leave blank to keep current): ").strip()
    new_price = float(new_price_str) if new_price_str else None

    print(f"Current Availability: {existing['availability']}")
    new_avail = input("New Availability (leave blank to keep current): ").strip()

    updated = db.update_product(
        product_id=product_id,
        title=new_title if new_title else None,
        price=new_price,
        availability=new_avail if new_avail else None
    )

    if updated:
        print("\nProduct updated successfully.")
    else:
        print("\nNo changes made.")

def handle_delete(db):
    print_header("Delete Product Record")
    id_str = input("Enter Product ID to delete: ").strip()
    if not id_str.isdigit():
        print("Invalid ID.")
        return

    product_id = int(id_str)
    existing = db.get_product_by_id(product_id)
    if not existing:
        print(f"No product found with ID {product_id}.")
        return

    confirm = input(f"Are you sure you want to delete '{existing['title']}'? (y/N): ").strip().lower()
    if confirm == "y":
        if db.delete_product(product_id):
            print("Product deleted successfully.")
        else:
            print("Failed to delete product.")
    else:
        print("Deletion canceled.")

def handle_export(db):
    print_header("Export Products to CSV")
    filename = input("Enter output CSV filename [products_export.csv]: ").strip()
    if not filename:
        filename = "products_export.csv"

    exported = db.export_to_csv(filename)
    if exported > 0:
        print(f"\nSuccessfully exported {exported} products to {filename}")
    else:
        print("\nNo products available to export.")

def handle_launch_dashboard():
    print_header("Launch Web Dashboard")
    print("Starting Flask web server...")
    print("Open your browser at: http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the web server and return.\n")
    from app import app
    app.run(debug=False, port=5000)

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "products.db")
    db = ProductDatabase(db_path)

    if db.get_total_count() < 30:
        print_header("Welcome to Product Market Research Tool")
        print(f"Current database has {db.get_total_count()} products (target: 30+).")
        auto_scrape = input("Would you like to scrape products now from Books to Scrape? (Y/n): ").strip().lower()
        if auto_scrape != "n":
            handle_scrape(db)
            input("\nPress Enter to continue to the main menu...")

    while True:
        print_header("Online Shop Market Research Tool")
        print("[1] Scrape Products from Practice Website (Collect 30+ items)")
        print("[2] View All Products")
        print("[3] Search Products by Name & Price Filter")
        print("[4] Display Cheapest & Most Expensive Products")
        print("[5] Display Market Statistics (Average Price & Total)")
        print("[6] Add Product Manually")
        print("[7] Update Product Information")
        print("[8] Delete Product Record")
        print("[9] Export Records to CSV")
        print("[10] Launch Web Dashboard (Flask)")
        print("[0] Exit")
        print("=" * 65)

        choice = input("Enter your choice (0-10): ").strip()

        if choice == "1":
            handle_scrape(db)
        elif choice == "2":
            handle_view_all(db)
        elif choice == "3":
            handle_search_filter(db)
        elif choice == "4":
            handle_price_extremes(db)
        elif choice == "5":
            handle_statistics(db)
        elif choice == "6":
            handle_manual_insert(db)
        elif choice == "7":
            handle_update(db)
        elif choice == "8":
            handle_delete(db)
        elif choice == "9":
            handle_export(db)
        elif choice == "10":
            handle_launch_dashboard()
        elif choice == "0":
            print("\nExiting Product Market Research Tool. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please select from 0 to 10.")

        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
