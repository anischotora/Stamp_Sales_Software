import customtkinter as ctk
from tkinter import messagebox, ttk

from database import get_categories, create_sale


class SalesWindow(ctk.CTkToplevel):

    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)

        self.parent = parent
        self.refresh_callback = refresh_callback
        self.categories = []
        self.category_map = {}
        self.sale_items = []

        self.title("New Stamp Sale")
        self.geometry("1250x800")
        self.minsize(1100, 700)

        self.transient(parent)
        self.lift()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.create_ui()
        self.load_categories()

    # =====================================================
    # UI
    # =====================================================

    def create_ui(self):
        self.configure(fg_color="#F1F5F9")

        header = ctk.CTkFrame(
            self,
            height=70,
            corner_radius=0,
            fg_color="#1E293B"
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="New Stamp Sale",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=18)

        ctk.CTkButton(
            header,
            text="Close",
            width=100,
            command=self.close_window,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        ).pack(side="right", padx=25)

        main = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )
        main.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # =====================================================
        # CUSTOMER INFORMATION
        # =====================================================

        customer_frame = ctk.CTkFrame(
            main,
            fg_color="white",
            corner_radius=12
        )
        customer_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=(18, 12)
        )

        customer_frame.grid_columnconfigure(0, weight=1)
        customer_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            customer_frame,
            text="Customer Name"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20
        )

        ctk.CTkLabel(
            customer_frame,
            text="Address"
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=10
        )

        self.customer_name_entry = ctk.CTkEntry(
            customer_frame,
            height=40,
            placeholder_text="Customer name"
        )
        self.customer_name_entry.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(20, 10),
            pady=(5, 20)
        )

        self.address_entry = ctk.CTkEntry(
            customer_frame,
            height=40,
            placeholder_text="Customer address"
        )
        self.address_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=(10, 20),
            pady=(5, 20)
        )

        # =====================================================
        # ADD STAMP ITEM
        # =====================================================

        item_frame = ctk.CTkFrame(
            main,
            fg_color="white",
            corner_radius=12
        )
        item_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            item_frame,
            text="Add Stamp Item",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0,
            column=0,
            columnspan=7,
            sticky="w",
            padx=20,
            pady=(18, 12)
        )

        for column in range(7):
            item_frame.grid_columnconfigure(column, weight=1)

        labels = [
            "Category",
            "Serial Number",
            "Available",
            "Quantity",
            "Stamp Price",
            "Profit Per Stamp",
            "Total Profit"
        ]

        for column, text in enumerate(labels):
            ctk.CTkLabel(
                item_frame,
                text=text
            ).grid(
                row=1,
                column=column,
                sticky="w",
                padx=8
            )

        self.category_combo = ctk.CTkComboBox(
            item_frame,
            values=["No Category"],
            state="readonly",
            height=40,
            command=self.category_changed
        )
        self.category_combo.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(20, 6),
            pady=(5, 15)
        )

        self.serial_entry = ctk.CTkEntry(
            item_frame,
            height=40,
            placeholder_text="Serial number"
        )
        self.serial_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=6,
            pady=(5, 15)
        )

        self.stock_label = ctk.CTkLabel(
            item_frame,
            text="0",
            height=40,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2563EB"
        )
        self.stock_label.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=6,
            pady=(5, 15)
        )

        self.quantity_entry = ctk.CTkEntry(
            item_frame,
            height=40,
            placeholder_text="Quantity"
        )
        self.quantity_entry.grid(
            row=2,
            column=3,
            sticky="ew",
            padx=6,
            pady=(5, 15)
        )

        self.stamp_price_label = ctk.CTkLabel(
            item_frame,
            text="৳ 0.00",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2563EB"
        )
        self.stamp_price_label.grid(
            row=2,
            column=4,
            sticky="ew",
            padx=6,
            pady=(5, 15)
        )

        self.profit_entry = ctk.CTkEntry(
            item_frame,
            height=40,
            placeholder_text="Profit each"
        )
        self.profit_entry.grid(
            row=2,
            column=5,
            sticky="ew",
            padx=6,
            pady=(5, 15)
        )

        self.calculated_profit_label = ctk.CTkLabel(
            item_frame,
            text="৳ 0.00",
            height=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#059669"
        )
        self.calculated_profit_label.grid(
            row=2,
            column=6,
            sticky="ew",
            padx=(6, 20),
            pady=(5, 15)
        )

        ctk.CTkButton(
            item_frame,
            text="ADD ITEM",
            height=42,
            command=self.add_item,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(
            row=3,
            column=0,
            columnspan=7,
            sticky="ew",
            padx=20,
            pady=(0, 20)
        )

        self.quantity_entry.bind(
            "<KeyRelease>",
            self.calculate_preview
        )

        self.profit_entry.bind(
            "<KeyRelease>",
            self.calculate_preview
        )

        # =====================================================
        # SALE ITEMS TABLE
        # =====================================================

        table_frame = ctk.CTkFrame(
            main,
            fg_color="white",
            corner_radius=12
        )
        table_frame.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        table_header = ctk.CTkFrame(
            table_frame,
            fg_color="transparent"
        )
        table_header.pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        ctk.CTkLabel(
            table_header,
            text="Sale Items",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            table_header,
            text="Remove Selected",
            width=150,
            command=self.remove_selected_item,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        ).pack(side="right")

        columns = (
            "category",
            "serial",
            "quantity",
            "stamp_price",
            "profit_each",
            "total_profit",
            "grand_total"
        )

        self.items_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8
        )

        headings = {
            "category": "Category",
            "serial": "Serial Number",
            "quantity": "Quantity",
            "stamp_price": "Stamp Price",
            "profit_each": "Profit Per Stamp",
            "total_profit": "Total Profit",
            "grand_total": "Grand Total"
        }

        for column, text in headings.items():
            self.items_tree.heading(column, text=text)

        self.items_tree.column(
            "category", anchor="center", width=120
        )
        self.items_tree.column(
            "serial", anchor="center", width=180
        )
        self.items_tree.column(
            "quantity", anchor="center", width=90
        )
        self.items_tree.column(
            "stamp_price", anchor="center", width=120
        )
        self.items_tree.column(
            "profit_each", anchor="center", width=130
        )
        self.items_tree.column(
            "total_profit", anchor="center", width=120
        )
        self.items_tree.column(
            "grand_total", anchor="center", width=120
        )

        self.items_tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 15)
        )

        # =====================================================
        # TOTAL
        # =====================================================

        bottom_frame = ctk.CTkFrame(
            main,
            fg_color="white",
            corner_radius=12
        )
        bottom_frame.pack(fill="x", pady=(0, 20))

        self.total_quantity_label = ctk.CTkLabel(
            bottom_frame,
            text="Total Quantity: 0",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.total_quantity_label.pack(
            side="left",
            padx=20,
            pady=20
        )

        self.total_stamp_price_label = ctk.CTkLabel(
            bottom_frame,
            text="Stamp Price: ৳ 0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2563EB"
        )
        self.total_stamp_price_label.pack(
            side="left",
            padx=15
        )

        self.total_profit_label = ctk.CTkLabel(
            bottom_frame,
            text="Profit: ৳ 0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#059669"
        )
        self.total_profit_label.pack(
            side="left",
            padx=15
        )

        self.grand_total_label = ctk.CTkLabel(
            bottom_frame,
            text="Grand Total: ৳ 0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#7C3AED"
        )
        self.grand_total_label.pack(
            side="left",
            padx=15
        )

        ctk.CTkButton(
            bottom_frame,
            text="SAVE SALE",
            width=170,
            height=45,
            command=self.save_sale,
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(
            side="right",
            padx=25,
            pady=15
        )

    # =====================================================
    # CATEGORY
    # =====================================================

    def load_categories(self):
        try:
            self.categories = get_categories(active_only=True)
            self.category_map = {}

            names = []

            for category in self.categories:
                name = str(category["name"])
                names.append(name)
                self.category_map[name] = category

            if names:
                self.category_combo.configure(values=names)
                self.category_combo.set(names[0])
                self.update_stock_label()
                self.calculate_preview()
            else:
                self.category_combo.configure(
                    values=["No Category"]
                )
                self.category_combo.set("No Category")
                self.stock_label.configure(text="0")

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                str(error),
                parent=self
            )

    def category_changed(self, selected_value=None):
        self.update_stock_label()
        self.calculate_preview()

    def update_stock_label(self):
        category = self.category_map.get(
            self.category_combo.get()
        )

        if category:
            self.stock_label.configure(
                text=str(category["current_stock"])
            )
        else:
            self.stock_label.configure(text="0")

    # =====================================================
    # PRICE CALCULATION
    # =====================================================

    def get_category_unit_price(self, category):
        if not category:
            return 0.0

        try:
            return float(str(category["name"]).strip())
        except (ValueError, TypeError):
            return 0.0

    def calculate_preview(self, event=None):
        category = self.category_map.get(
            self.category_combo.get()
        )

        unit_price = self.get_category_unit_price(category)

        try:
            quantity = int(
                self.quantity_entry.get().strip()
            )
            if quantity < 0:
                quantity = 0
        except ValueError:
            quantity = 0

        try:
            profit_per_stamp = float(
                self.profit_entry.get().strip()
            )
            if profit_per_stamp < 0:
                profit_per_stamp = 0.0
        except ValueError:
            profit_per_stamp = 0.0

        stamp_price = unit_price * quantity
        total_profit = profit_per_stamp * quantity

        self.stamp_price_label.configure(
            text=f"৳ {stamp_price:,.2f}"
        )

        self.calculated_profit_label.configure(
            text=f"৳ {total_profit:,.2f}"
        )

    # =====================================================
    # ADD ITEM
    # =====================================================

    def add_item(self):
        category_name = self.category_combo.get()
        category = self.category_map.get(category_name)

        if not category:
            messagebox.showwarning(
                "Category",
                "Please select a valid category.",
                parent=self
            )
            return

        serial_number = self.serial_entry.get().strip()

        if not serial_number:
            messagebox.showwarning(
                "Serial Number",
                "Please enter a serial number for this category.",
                parent=self
            )
            return

        try:
            quantity = int(
                self.quantity_entry.get().strip()
            )

            if quantity <= 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Quantity",
                "Please enter a valid quantity.",
                parent=self
            )
            return

        try:
            profit_per_stamp = float(
                self.profit_entry.get().strip()
            )

            if profit_per_stamp < 0:
                raise ValueError

        except ValueError:
            messagebox.showwarning(
                "Invalid Profit",
                "Please enter a valid profit per stamp.",
                parent=self
            )
            return

        available_stock = int(
            category["current_stock"]
        )

        already_added = sum(
            int(item["quantity"])
            for item in self.sale_items
            if int(item["category_id"]) == int(category["id"])
        )

        if already_added + quantity > available_stock:
            messagebox.showwarning(
                "Not Enough Stock",
                (
                    f"Available stock: {available_stock}\n"
                    f"Already added: {already_added}\n"
                    f"New quantity: {quantity}"
                ),
                parent=self
            )
            return

        unit_price = self.get_category_unit_price(category)
        stamp_price = unit_price * quantity

        # IMPORTANT:
        # Profit entered is PROFIT PER STAMP.
        total_item_profit = profit_per_stamp * quantity

        grand_total = stamp_price + total_item_profit

        self.sale_items.append({
            "category_id": int(category["id"]),
            "category_name": str(category["name"]),
            "serial_number": serial_number,
            "quantity": quantity,
            "unit_price": unit_price,
            "stamp_price": stamp_price,
            "profit_per_stamp": profit_per_stamp,
            "profit": total_item_profit,
            "grand_total": grand_total
        })

        self.serial_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")
        self.profit_entry.delete(0, "end")

        self.stamp_price_label.configure(
            text="৳ 0.00"
        )
        self.calculated_profit_label.configure(
            text="৳ 0.00"
        )

        self.refresh_items_table()
        self.serial_entry.focus()

    # =====================================================
    # TABLE
    # =====================================================

    def refresh_items_table(self):
        for row in self.items_tree.get_children():
            self.items_tree.delete(row)

        total_quantity = 0
        total_stamp_price = 0.0
        total_profit = 0.0
        grand_total = 0.0

        for index, item in enumerate(self.sale_items):
            self.items_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    item["category_name"],
                    item["serial_number"],
                    item["quantity"],
                    f"৳ {item['stamp_price']:,.2f}",
                    f"৳ {item['profit_per_stamp']:,.2f}",
                    f"৳ {item['profit']:,.2f}",
                    f"৳ {item['grand_total']:,.2f}"
                )
            )

            total_quantity += item["quantity"]
            total_stamp_price += item["stamp_price"]
            total_profit += item["profit"]
            grand_total += item["grand_total"]

        self.total_quantity_label.configure(
            text=f"Total Quantity: {total_quantity}"
        )

        self.total_stamp_price_label.configure(
            text=f"Stamp Price: ৳ {total_stamp_price:,.2f}"
        )

        self.total_profit_label.configure(
            text=f"Profit: ৳ {total_profit:,.2f}"
        )

        self.grand_total_label.configure(
            text=f"Grand Total: ৳ {grand_total:,.2f}"
        )

    def remove_selected_item(self):
        selected = self.items_tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an item to remove.",
                parent=self
            )
            return

        index = int(selected[0])

        if 0 <= index < len(self.sale_items):
            self.sale_items.pop(index)
            self.refresh_items_table()

    # =====================================================
    # SAVE SALE
    # =====================================================

    def save_sale(self):
        customer_name = (
            self.customer_name_entry.get().strip()
        )

        customer_address = (
            self.address_entry.get().strip()
        )

        if not customer_name:
            messagebox.showwarning(
                "Customer Name",
                "Please enter customer name.",
                parent=self
            )
            return

        if not self.sale_items:
            messagebox.showwarning(
                "Sale Items",
                "Please add at least one stamp item.",
                parent=self
            )
            return

        total_quantity = sum(
            item["quantity"]
            for item in self.sale_items
        )

        total_stamp_price = sum(
            item["stamp_price"]
            for item in self.sale_items
        )

        total_profit = sum(
            item["profit"]
            for item in self.sale_items
        )

        grand_total = (
            total_stamp_price +
            total_profit
        )

        confirm = messagebox.askyesno(
            "Confirm Sale",
            (
                f"Customer: {customer_name}\n"
                f"Total Quantity: {total_quantity}\n"
                f"Stamp Price: ৳ {total_stamp_price:,.2f}\n"
                f"Total Profit: ৳ {total_profit:,.2f}\n"
                f"Grand Total: ৳ {grand_total:,.2f}\n\n"
                "Do you want to save this sale?"
            ),
            parent=self
        )

        if not confirm:
            return

        success, message = create_sale(
            customer_name,
            customer_address,
            self.sale_items
        )

        if success:
            messagebox.showinfo(
                "Sale Saved",
                message,
                parent=self
            )

            self.clear_form()
            self.load_categories()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Sale Error",
                message,
                parent=self
            )

    def clear_form(self):
        self.customer_name_entry.delete(0, "end")
        self.address_entry.delete(0, "end")
        self.serial_entry.delete(0, "end")
        self.quantity_entry.delete(0, "end")
        self.profit_entry.delete(0, "end")

        self.sale_items.clear()

        self.stamp_price_label.configure(
            text="৳ 0.00"
        )

        self.calculated_profit_label.configure(
            text="৳ 0.00"
        )

        self.refresh_items_table()
        self.customer_name_entry.focus()

    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()
