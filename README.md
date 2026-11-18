# Product Market Research Tool

A Python-based market research tool designed for online shop owners to automatically collect, manage, analyze, and export product records from permitted web sources.

---

## Target Source

- **Target Website**: [Books to Scrape](http://books.toscrape.com/)
- **Nature**: A dedicated, publicly permitted practice sandbox designed for testing and learning web scrapers.
- **Ethics & Rate Limiting**: Polite delays between requests, standard headers, and duplicate URL prevention.

---

## Features

- **Automated Web Scraping**: Extracts product name, price, stock status, and product URLs across pages.
- **SQLite Database Storage**: Automatically creates and manages a structured `products` table with primary keys and unique URL constraints.
- **CRUD Operations**: Full SQL support to create, view, search, update, and delete products.
- **Market Analytics**:
  - Computes average product price using SQL.
  - Identifies cheapest and most expensive products.
  - Computes total stored records and price distribution.
- **Search & Filter**: Find products by keyword and filter dynamically by price range.
- **Duplicate Prevention**: Avoids saving duplicate products through unique constraints and set tracking.
- **Bonus Challenge - CSV Export**: One-click export of database records to CSV format.
- **Bonus Challenge - Web Dashboard**: Built-in Flask web application with a responsive dashboard interface.

---

## Project Structure

```text
Project 4/
├── database.py         # SQLite database management and CRUD operations
├── scraper.py          # Web scraper for Books to Scrape
├── main.py             # Interactive CLI application
├── app.py              # Flask web dashboard application
├── test_project.py     # Unit test suite
├── requirements.txt    # Python dependencies
├── .gitignore          # Ignored cache and temporary files
├── templates/
│   └── index.html      # Dashboard HTML template (Bootstrap 5)
└── README.md           # Documentation and usage guide
```

---

## Prerequisites & Installation

### 1. Clone or Open the Repository
```bash
git clone https://github.com/anki7tt/Arena-Web-Security-Py12-Project-4.git
cd "Project 4"
```

### 2. Install Dependencies
Make sure you have Python 3.8+ installed, then run:

```bash
pip install -r requirements.txt
```

Required packages:
- `requests`: HTTP requests for web scraping
- `beautifulsoup4`: HTML parsing and data extraction
- `Flask`: Lightweight web framework for the dashboard

---

## How to Run

### Option 1: Interactive Console Application (CLI)

Run the main command-line interface:

```bash
python main.py
```

The CLI menu offers the following options:
```text
=================================================================
                 ONLINE SHOP MARKET RESEARCH TOOL                 
=================================================================
[1] Scrape Products from Practice Website (Collect 30+ items)
[2] View All Products
[3] Search Products by Name & Price Filter
[4] Display Cheapest & Most Expensive Products
[5] Display Market Statistics (Average Price & Total)
[6] Add Product Manually
[7] Update Product Information
[8] Delete Product Record
[9] Export Records to CSV
[10] Launch Web Dashboard (Flask)
[0] Exit
=================================================================
```

### Option 2: Web Dashboard (Flask)

Start the web application directly:

```bash
python app.py
```

Then open your browser and navigate to:
```text
http://127.0.0.1:5000
```

From the web dashboard you can:
- View summary metric cards (Total Products, Average Price, Cheapest, Most Expensive).
- Filter products by keyword and price range.
- Scrape latest books on-demand.
- Add and delete products.
- Export all records to CSV directly via the "Export CSV" button.

---

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    availability TEXT NOT NULL,
    product_url TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Running Unit Tests

Run the test suite to verify database operations, duplicate detection, and scraping parsers:

```bash
python test_project.py
```
