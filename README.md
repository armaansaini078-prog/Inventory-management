# Inventory Management System (Python + Tkinter + SQLite)

## Features
- Dashboard with product count, total units, stock valuation, and low-stock count
- Add, view, search, update, and delete products
- Stock In and Stock Out with quantity validation
- Low-stock list and product-wise inventory valuation report
- SQLite persistence and stock movement history

## Requirements
- Python 3.10 or newer recommended
- Tkinter (included with most Windows Python installations)
- SQLite (included with Python's `sqlite3` module)

No third-party packages are required.

## Run on Windows
1. Install Python from https://www.python.org/downloads/ and tick **Add Python to PATH** during setup.
2. Extract/open the `InventoryManagementSystem` folder.
3. Open Command Prompt or the VS Code terminal in that folder.
4. Run:
   ```bash
   python main.py
   ```
   If `python` does not work, try `py main.py`.
5. The `inventory.db` database is created automatically beside the Python files.

## How to use
1. Open **Products**, fill in product details and click **Add Product**.
2. Select a row in the product table to load it into the form. Edit values and choose **Update Selected** to save.
3. Select a product and choose **Delete Selected** to remove it.
4. Use **Stock Movement** to record Stock In or Stock Out. Stock Out cannot reduce stock below zero.
5. Check **Dashboard** for low-stock items and **Reports** for total inventory valuation.

## Project explanation (Hinglish)
- `main.py`: Tkinter se application window, tabs, forms, tables aur buttons bante hain. User ke actions par database functions call hote hain.
- `database.py`: SQLite database create karta hai aur product add/update/delete, search, stock movement aur report calculations handle karta hai.
- `inventory.db`: Actual data file hai. App close karne ke baad bhi records save rehte hain. Is file ko delete karne par stored records delete ho jayenge.
- `products` table product details aur current quantity rakhti hai.
- `stock_movements` table Stock In/Out ka history rakhti hai.
- SQL queries parameterized hain, aur Stock Out se negative stock nahi ho sakta.

## Database design
`products(id, name, category, price, quantity, supplier, low_stock_level, created_at)`

`stock_movements(id, product_id, movement_type, quantity, note, created_at)`

Relationship: one product can have many stock movement records.

## Important note
This is an educational single-computer project, not a multi-user production accounting system. Keep a backup of `inventory.db` if the data matters.
