"""Inventory Management System - Tkinter desktop application."""
import tkinter as tk
from tkinter import ttk, messagebox
import database as db

BG = "#f3f6fb"
NAVY = "#183153"
BLUE = "#2563eb"


class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("1120x720")
        self.minsize(950, 620)
        self.configure(bg=BG)
        db.init_db()
        self.selected_product_id = None
        self._style()
        self._build_ui()
        self.refresh_all()

    def _style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), foreground=NAVY)
        style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#64748b")
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 6))
        style.configure("Primary.TButton", background=BLUE, foreground="white")
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])
        style.configure("Treeview", rowheight=29, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TNotebook.Tab", padding=(16, 9), font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        header = ttk.Frame(self, padding=(22, 18, 22, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Inventory Management System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Manage products, stock movement and inventory reports", style="Sub.TLabel").pack(anchor="w", pady=(3, 0))
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(8, 18))
        self.dashboard_tab = ttk.Frame(self.notebook, padding=16)
        self.products_tab = ttk.Frame(self.notebook, padding=16)
        self.stock_tab = ttk.Frame(self.notebook, padding=16)
        self.reports_tab = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.products_tab, text="Products")
        self.notebook.add(self.stock_tab, text="Stock Movement")
        self.notebook.add(self.reports_tab, text="Reports")
        self._build_dashboard()
        self._build_products()
        self._build_stock()
        self._build_reports()

    def _build_dashboard(self):
        ttk.Label(self.dashboard_tab, text="Overview", style="Title.TLabel").pack(anchor="w", pady=(0, 12))
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x")
        self.stat_labels = {}
        for key, title in [("product_count", "Product Types"), ("total_units", "Total Units"), ("inventory_value", "Inventory Value (₹)"), ("low_stock_count", "Low Stock Items")]:
            card = tk.Frame(cards, bg="white", highlightbackground="#dce4ef", highlightthickness=1, padx=16, pady=14)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(card, text=title, bg="white", fg="#64748b", font=("Segoe UI", 10)).pack(anchor="w")
            value = tk.Label(card, text="0", bg="white", fg=NAVY, font=("Segoe UI", 21, "bold"))
            value.pack(anchor="w", pady=(8, 0))
            self.stat_labels[key] = value
        ttk.Label(self.dashboard_tab, text="Low Stock Products", style="Title.TLabel").pack(anchor="w", pady=(24, 10))
        self.low_tree = self._make_tree(self.dashboard_tab, ("id", "name", "category", "quantity", "level"), ("ID", "Product", "Category", "Quantity", "Alert At"), height=9)
        ttk.Button(self.dashboard_tab, text="Refresh Dashboard", command=self.refresh_all).pack(anchor="e", pady=(10, 0))

    def _build_products(self):
        ttk.Label(self.products_tab, text="Product Management", style="Title.TLabel").pack(anchor="w")
        form = ttk.LabelFrame(self.products_tab, text="Product Details", padding=12)
        form.pack(fill="x", pady=(12, 10))
        self.fields = {}
        specs = [("name", "Product Name"), ("category", "Category"), ("price", "Price (₹)"), ("quantity", "Quantity"), ("supplier", "Supplier"), ("low_stock_level", "Low-stock level")]
        for i, (key, label) in enumerate(specs):
            r, c = divmod(i, 3)
            ttk.Label(form, text=label).grid(row=r * 2, column=c, sticky="w", padx=8, pady=(3, 2))
            entry = ttk.Entry(form, width=28)
            entry.grid(row=r * 2 + 1, column=c, sticky="ew", padx=8, pady=(0, 7))
            self.fields[key] = entry
            form.columnconfigure(c, weight=1)
        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=3, sticky="w", padx=8, pady=(3, 0))
        ttk.Button(buttons, text="Add Product", style="Primary.TButton", command=self.add_product).pack(side="left", padx=(0, 7))
        ttk.Button(buttons, text="Update Selected", command=self.update_product).pack(side="left", padx=(0, 7))
        ttk.Button(buttons, text="Delete Selected", command=self.delete_product).pack(side="left", padx=(0, 7))
        ttk.Button(buttons, text="Clear Form", command=self.clear_form).pack(side="left")
        searchrow = ttk.Frame(self.products_tab)
        searchrow.pack(fill="x", pady=(0, 8))
        ttk.Label(searchrow, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search = ttk.Entry(searchrow, textvariable=self.search_var, width=34)
        search.pack(side="left", padx=8)
        search.bind("<KeyRelease>", lambda _e: self.refresh_products())
        ttk.Button(searchrow, text="Show All", command=self.reset_search).pack(side="left")
        ttk.Button(searchrow, text="Low Stock Only", command=self.show_low_stock).pack(side="left", padx=8)
        cols = ("id", "name", "category", "price", "quantity", "supplier", "low_stock_level")
        self.product_tree = self._make_tree(self.products_tab, cols, ("ID", "Product Name", "Category", "Price (₹)", "Quantity", "Supplier", "Alert At"), height=10)
        self.product_tree.bind("<<TreeviewSelect>>", self.on_product_select)

    def _build_stock(self):
        ttk.Label(self.stock_tab, text="Stock In / Stock Out", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.stock_tab, text="Stock In = naya stock aaya; Stock Out = sale ya stock use hua.", style="Sub.TLabel").pack(anchor="w", pady=(4, 16))
        form = ttk.LabelFrame(self.stock_tab, text="Record Stock Movement", padding=16)
        form.pack(fill="x", anchor="n")
        ttk.Label(form, text="Product").grid(row=0, column=0, sticky="w", padx=8, pady=6)
        self.stock_product = ttk.Combobox(form, state="readonly", width=42)
        self.stock_product.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 10))
        ttk.Label(form, text="Movement Type").grid(row=0, column=1, sticky="w", padx=8, pady=6)
        self.stock_type = ttk.Combobox(form, state="readonly", values=["Stock In", "Stock Out"], width=20)
        self.stock_type.current(0)
        self.stock_type.grid(row=1, column=1, sticky="ew", padx=8, pady=(0, 10))
        ttk.Label(form, text="Quantity").grid(row=2, column=0, sticky="w", padx=8, pady=6)
        self.stock_qty = ttk.Entry(form, width=25)
        self.stock_qty.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 10))
        ttk.Label(form, text="Note (optional)").grid(row=2, column=1, sticky="w", padx=8, pady=6)
        self.stock_note = ttk.Entry(form, width=35)
        self.stock_note.grid(row=3, column=1, sticky="ew", padx=8, pady=(0, 10))
        ttk.Button(form, text="Save Stock Movement", style="Primary.TButton", command=self.save_stock_movement).grid(row=4, column=0, sticky="w", padx=8, pady=8)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)
        ttk.Label(self.stock_tab, text="Recent Stock Movements", style="Title.TLabel").pack(anchor="w", pady=(22, 10))
        self.movement_tree = self._make_tree(self.stock_tab, ("id", "product_name", "movement_type", "quantity", "note", "created_at"), ("ID", "Product", "Type", "Quantity", "Note", "Date"), height=11)

    def _build_reports(self):
        ttk.Label(self.reports_tab, text="Inventory Reports", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.reports_tab, text="Current inventory valuation and stock summary.", style="Sub.TLabel").pack(anchor="w", pady=(4, 12))
        self.report_summary = tk.Label(self.reports_tab, text="", justify="left", anchor="w", bg="white", fg=NAVY, font=("Segoe UI", 12), padx=18, pady=18, relief="solid", bd=1)
        self.report_summary.pack(fill="x", pady=(0, 16))
        ttk.Button(self.reports_tab, text="Refresh Report", command=self.refresh_all).pack(anchor="w")
        ttk.Label(self.reports_tab, text="Product-wise stock", style="Title.TLabel").pack(anchor="w", pady=(20, 10))
        self.report_tree = self._make_tree(self.reports_tab, ("id", "name", "category", "price", "quantity", "value"), ("ID", "Product", "Category", "Unit Price (₹)", "Quantity", "Stock Value (₹)"), height=12)

    def _make_tree(self, parent, columns, headings, height=10):
        wrapper = ttk.Frame(parent)
        wrapper.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrapper, columns=columns, show="headings", height=height)
        yscroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        xscroll = ttk.Scrollbar(wrapper, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=115, minwidth=75, anchor="w")
        tree.column(columns[0], width=55, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        wrapper.rowconfigure(0, weight=1)
        wrapper.columnconfigure(0, weight=1)
        return tree

    def _form_values(self):
        name = self.fields["name"].get().strip()
        if not name:
            raise ValueError("Product Name bharna zaroori hai.")
        category = self.fields["category"].get().strip()
        supplier = self.fields["supplier"].get().strip()
        try:
            price = float(self.fields["price"].get())
            quantity = int(self.fields["quantity"].get())
            low = int(self.fields["low_stock_level"].get() or "5")
        except ValueError:
            raise ValueError("Price number mein aur Quantity/Low-stock level whole number mein daalein.")
        if price < 0 or quantity < 0 or low < 0:
            raise ValueError("Price aur quantities negative nahi ho sakti.")
        return name, category, price, quantity, supplier, low

    def add_product(self):
        try:
            values = self._form_values()
            db.add_product(*values)
            messagebox.showinfo("Success", "Product successfully add ho gaya.")
            self.clear_form()
            self.refresh_all()
        except (ValueError, Exception) as exc:
            messagebox.showerror("Error", str(exc))

    def update_product(self):
        if self.selected_product_id is None:
            messagebox.showwarning("Select Product", "Pehle table se product select karein.")
            return
        try:
            db.update_product(self.selected_product_id, *self._form_values())
            messagebox.showinfo("Success", "Product update ho gaya.")
            self.clear_form()
            self.refresh_all()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_product(self):
        if self.selected_product_id is None:
            messagebox.showwarning("Select Product", "Delete karne ke liye product select karein.")
            return
        if messagebox.askyesno("Confirm Delete", "Kya aap selected product delete karna chahte hain?"):
            db.delete_product(self.selected_product_id)
            self.clear_form()
            self.refresh_all()
            messagebox.showinfo("Deleted", "Product delete ho gaya.")

    def clear_form(self):
        self.selected_product_id = None
        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.fields["quantity"].insert(0, "0")
        self.fields["low_stock_level"].insert(0, "5")
        for item in self.product_tree.selection():
            self.product_tree.selection_remove(item)

    def on_product_select(self, _event=None):
        selection = self.product_tree.selection()
        if not selection:
            return
        row = self.product_tree.item(selection[0], "values")
        product = db.get_product(int(row[0]))
        if product is None:
            return
        self.selected_product_id = product["id"]
        for key in self.fields:
            self.fields[key].delete(0, tk.END)
            self.fields[key].insert(0, str(product[key]))

    def reset_search(self):
        self.search_var.set("")
        self.refresh_products()

    def show_low_stock(self):
        self.search_var.set("")
        self._populate_products(db.list_products(low_only=True))

    def refresh_products(self):
        self._populate_products(db.list_products(self.search_var.get()))

    def _populate_products(self, products):
        self.product_tree.delete(*self.product_tree.get_children())
        for p in products:
            self.product_tree.insert("", "end", values=(p["id"], p["name"], p["category"], f'{p["price"]:.2f}', p["quantity"], p["supplier"], p["low_stock_level"]))

    def save_stock_movement(self):
        selected = self.stock_product.get()
        if not selected:
            messagebox.showwarning("Select Product", "Product select karein.")
            return
        try:
            product_id = int(selected.split(" | ", 1)[0])
            quantity = int(self.stock_qty.get())
            movement = "IN" if self.stock_type.get() == "Stock In" else "OUT"
            db.move_stock(product_id, movement, quantity, self.stock_note.get())
            self.stock_qty.delete(0, tk.END)
            self.stock_note.delete(0, tk.END)
            self.refresh_all()
            messagebox.showinfo("Success", "Stock movement save ho gaya.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def refresh_all(self):
        stats = db.dashboard_stats()
        self.stat_labels["product_count"].config(text=str(stats["product_count"]))
        self.stat_labels["total_units"].config(text=str(stats["total_units"]))
        self.stat_labels["inventory_value"].config(text=f'₹{stats["inventory_value"]:,.2f}')
        self.stat_labels["low_stock_count"].config(text=str(stats["low_stock_count"]))
        low_products = db.list_products(low_only=True)
        self.low_tree.delete(*self.low_tree.get_children())
        for p in low_products:
            self.low_tree.insert("", "end", values=(p["id"], p["name"], p["category"], p["quantity"], p["low_stock_level"]))
        self.refresh_products()
        products = db.list_products()
        self.stock_product["values"] = [f'{p["id"]} | {p["name"]} (Stock: {p["quantity"]})' for p in products]
        self.movement_tree.delete(*self.movement_tree.get_children())
        for m in db.movement_history():
            self.movement_tree.insert("", "end", values=(m["id"], m["product_name"], "Stock In" if m["movement_type"] == "IN" else "Stock Out", m["quantity"], m["note"], m["created_at"]))
        self.report_summary.config(text=(
            f'Product types: {stats["product_count"]}\n'
            f'Total units in stock: {stats["total_units"]}\n'
            f'Total inventory value: ₹{stats["inventory_value"]:,.2f}\n'
            f'Products at/below low-stock level: {stats["low_stock_count"]}\n\n'
            'Inventory value = unit price × quantity, summed across all products.'
        ))
        self.report_tree.delete(*self.report_tree.get_children())
        for p in products:
            self.report_tree.insert("", "end", values=(p["id"], p["name"], p["category"], f'{p["price"]:.2f}', p["quantity"], f'{p["price"] * p["quantity"]:.2f}'))


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()
