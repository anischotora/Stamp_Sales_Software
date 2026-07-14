
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
        self.geometry("1200x780")
        self.minsize(1050, 680)

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

        # HEADER
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

        # MAIN
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
        customer_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            padx=20,
            pady=(18, 12)
        )

        for column in range(3):
            customer_frame.grid_columnconfigure(
                column,
                weight=1
            )

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

        ctk.CTkLabel(
            customer_frame,
            text="Serial Number"
        ).grid(
            row=1,
            column=2,
            sticky="w",
            padx=20
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
            padx=10,
            pady=(5, 20)
        )

        self.serial_entry = ctk.CTkEntry(
            customer_frame,
            height=40,
            placeholder_text="Example: কব 3595820"
        )
        self.serial_entry.grid(
            row=2,
            column=2,
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
        item_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            item_frame,
            text="Add Stamp Item",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(
            row=0,
            column=0,
            columnspan=6,
            sticky="w",
            padx=20,
            pady=(18, 12)
        )

        for column in range(5):
            item_frame.grid_columnconfigure(
                column,
                weight=1
            )

        # LABELS
        labels = [
            "Category",
            "Available Stock",
            "Quantity",
            "Profit Per Stamp",
            "Calculated Profit"
        ]

        for column, text in enumerate(labels):
            ctk.CTkLabel(
                item_frame,
                text=text
            ).grid(
                row=1,
                column=column,
                sticky="w",
                padx=10
            )

        # CATEGORY
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
            padx=(20, 10),
            pady=(5, 20)
        )

        # STOCK
        self.stock_label = ctk.CTkLabel(
            item_frame,
            text="0",
            height=40,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color="#2563EB"
        )
        self.stock_label.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=(5, 20)
        )

        # QUANTITY
        self.quantity_entry = ctk.CTkEntry(
            item_frame,
            height=40,
            placeholder_text="Quantity"
        )
        self.quantity_entry.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=10,
            pady=(5, 20)
        )

        # PROFIT PER STAMP
        self.profit_entry = ctk.CTkEntry(
            item_frame,
            height=40,
            placeholder_text="Profit each"
        )
        self.profit_entry.grid(
            row=2,
            column=3,
            sticky="ew",
            padx=10,
            pady=(5, 20)
        )

        # CALCULATED PROFIT
        self.calculated_profit_label = ctk.CTkLabel(
            item_frame,
            text="৳ 0.00",
            height=40,
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color="#059669"
        )
        self.calculated_profit_label.grid(
            row=2,
            column=4,
            sticky="ew",
            padx=10,
            pady=(5, 20)
        )

        # ADD BUTTON
        ctk.CTkButton(
            item_frame,
            text="Add Item",
            width=120,
            height=40,
            command=self.add_item,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        ).grid(
            row=2,
            column=5,
            padx=(10, 20),
            pady=(5, 20)
        )

        # LIVE CALCULATION
        self.quantity_entry.bind(
            "<KeyRelease>",
            self.calculate_profit_preview
        )

        self.profit_entry.bind(
            "<KeyRelease>",
            self.calculate_profit_preview
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
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
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
            "quantity",
            "profit_per_stamp",
            "total_profit"
        )

        self.items_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.items_tree.heading(
            "category",
            text="Stamp Category"
        )

        self.items_tree.heading(
            "quantity",
            text="Quantity"
        )

        self.items_tree.heading(
            "profit_per_stamp",
            text="Profit Per Stamp"
        )

        self.items_tree.heading(
            "total_profit",
            text="Total Profit"
        )

        self.items_tree.column(
            "category",
            anchor="center",
            width=250
        )

        self.items_tree.column(
            "quantity",
            anchor="center",
            width=150
        )

        self.items_tree.column(
            "profit_per_stamp",
            anchor="center",
            width=180
        )

        self.items_tree.column(
            "total_profit",
            anchor="center",
            width=180
        )

        self.items_tree.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(5, 15)
        )

        # =====================================================
        # TOTAL / SAVE
        # =====================================================

        bottom_frame = ctk.CTkFrame(
            main,
            fg_color="white",
            corner_radius=12
        )
        bottom_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        self.total_quantity_label = ctk.CTkLabel(
            bottom_frame,
            text="Total Quantity: 0",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            )
        )
        self.total_quantity_label.pack(
            side="left",
            padx=25,
            pady=20
        )

        self.total_profit_label = ctk.CTkLabel(
            bottom_frame,
            text="Total Profit: ৳ 0.00",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color="#059669"
        )
        self.total_profit_label.pack(
            side="left",
            padx=25,
            pady=20
        )

        ctk.CTkButton(
            bottom_frame,
            text="SAVE SALE",
            width=170,
            height=45,
            command=self.save_sale,
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            )
        ).pack(
            side="right",
            padx=25,
            pady=15
        )

    # =====================================================
    # LOAD CATEGORIES
    # =====================================================

    def load_categories(self):
        try:
            self.categories = get_categories(
                active_only=True
            )

            self.category_map = {}

            names = []

            for category in self.categories:
                name = str(category["name"])

                names.append(name)

                self.category_map[name] = category

            if names:
                self.category_combo.configure(
                    values=names
                )

                self.category_combo.set(
                    names[0]
                )

                self.update_stock_label()

            else:
                self.category_combo.configure(
                    values=["No Category"]
                )

                self.category_combo.set(
                    "No Category"
                )

                self.stock_label.configure(
                    text="0"
                )

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                str(error),
                parent=self
            )

    # =====================================================
    # CATEGORY CHANGE
    # =====================================================

    def category_changed(
        self,
        selected_value
    ):
        self.update_stock_label()

    def update_stock_label(self):
        category = self.category_map.get(
            self.category_combo.get()
        )

        if category:
            self.stock_label.configure(
                text=str(
                    category["current_stock"]
                )
            )
        else:
            self.stock_label.configure(
                text="0"
            )

    # =====================================================
    # LIVE PROFIT CALCULATION
    # =====================================================

    def calculate_profit_preview(
        self,
        event=None
    ):
        quantity_text = (
            self.quantity_entry.get().strip()
        )

        profit_text = (
            self.profit_entry.get().strip()
        )

        try:
            quantity = int(quantity_text)
            profit_per_stamp = float(profit_text)

            if quantity < 0:
                quantity = 0

            if profit_per_stamp < 0:
                profit_per_stamp = 0

            total_profit = (
                quantity *
                profit_per_stamp
            )

        except ValueError:
            total_profit = 0.0

        self.calculated_profit_label.configure(
            text=f"৳ {total_profit:,.2f}"
        )

    # =====================================================
    # ADD ITEM
    # =====================================================

    def add_item(self):
        category_name = (
            self.category_combo.get()
        )

        category = self.category_map.get(
            category_name
        )

        if not category:
            messagebox.showwarning(
                "Category",
                "Please select a valid category.",
                parent=self
            )
            return

        quantity_text = (
            self.quantity_entry.get().strip()
        )

        profit_text = (
            self.profit_entry.get().strip()
        )

        # QUANTITY VALIDATION
        try:
            quantity = int(
                quantity_text
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

        # PROFIT PER STAMP VALIDATION
        try:
            profit_per_stamp = float(
                profit_text
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

        # CALCULATE TOTAL PROFIT
        total_item_profit = (
            quantity *
            profit_per_stamp
        )

        available_stock = int(
            category["current_stock"]
        )

        already_added = sum(
            item["quantity"]
            for item in self.sale_items
            if item["category_id"]
            == category["id"]
        )

        if (
            already_added +
            quantity >
            available_stock
        ):
            messagebox.showwarning(
                "Not Enough Stock",
                (
                    f"Available stock: "
                    f"{available_stock}\n"
                    f"Already added: "
                    f"{already_added}\n"
                    f"New quantity: "
                    f"{quantity}"
                ),
                parent=self
            )
            return

        # SAME CATEGORY EXISTS
        existing_item = None

        for item in self.sale_items:
            if (
                item["category_id"]
                == category["id"]
            ):
                existing_item = item
                break

        if existing_item:
            # Combine quantity and total profit
            existing_item["quantity"] += (
                quantity
            )

            existing_item["profit"] += (
                total_item_profit
            )

            # Average profit per stamp for display
            if existing_item["quantity"] > 0:
                existing_item[
                    "profit_per_stamp"
                ] = (
                    existing_item["profit"] /
                    existing_item["quantity"]
                )

        else:
            self.sale_items.append({
                "category_id":
                    category["id"],

                "category_name":
                    category["name"],

                "quantity":
                    quantity,

                "profit_per_stamp":
                    profit_per_stamp,

                # database receives total profit
                "profit":
                    total_item_profit
            })

        self.quantity_entry.delete(
            0,
            "end"
        )

        self.profit_entry.delete(
            0,
            "end"
        )

        self.calculated_profit_label.configure(
            text="৳ 0.00"
        )

        self.refresh_items_table()

    # =====================================================
    # REFRESH ITEMS TABLE
    # =====================================================

    def refresh_items_table(self):
        for row in (
            self.items_tree.get_children()
        ):
            self.items_tree.delete(
                row
            )

        total_quantity = 0
        total_profit = 0.0

        for index, item in enumerate(
            self.sale_items
        ):
            self.items_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    item["category_name"],

                    item["quantity"],

                    (
                        f"৳ "
                        f"{item['profit_per_stamp']:,.2f}"
                    ),

                    (
                        f"৳ "
                        f"{item['profit']:,.2f}"
                    )
                )
            )

            total_quantity += (
                item["quantity"]
            )

            total_profit += (
                item["profit"]
            )

        self.total_quantity_label.configure(
            text=(
                f"Total Quantity: "
                f"{total_quantity}"
            )
        )

        self.total_profit_label.configure(
            text=(
                f"Total Profit: "
                f"৳ {total_profit:,.2f}"
            )
        )

    # =====================================================
    # REMOVE ITEM
    # =====================================================

    def remove_selected_item(self):
        selected = (
            self.items_tree.selection()
        )

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select an item to remove.",
                parent=self
            )
            return

        index = int(
            selected[0]
        )

        if (
            0 <= index <
            len(self.sale_items)
        ):
            self.sale_items.pop(
                index
            )

            self.refresh_items_table()

    # =====================================================
    # SAVE SALE
    # =====================================================

    def save_sale(self):
        customer_name = (
            self.customer_name_entry
            .get()
            .strip()
        )

        customer_address = (
            self.address_entry
            .get()
            .strip()
        )

        serial_number = (
            self.serial_entry
            .get()
            .strip()
        )

        if not customer_name:
            messagebox.showwarning(
                "Customer Name",
                "Please enter customer name.",
                parent=self
            )
            return

        if not serial_number:
            messagebox.showwarning(
                "Serial Number",
                "Please enter serial number.",
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

        total_profit = sum(
            item["profit"]
            for item in self.sale_items
        )

        confirm = messagebox.askyesno(
            "Confirm Sale",
            (
                f"Customer: "
                f"{customer_name}\n"

                f"Serial: "
                f"{serial_number}\n"

                f"Total Quantity: "
                f"{total_quantity}\n"

                f"Total Profit: "
                f"৳ {total_profit:,.2f}\n\n"

                "Do you want to save this sale?"
            ),
            parent=self
        )

        if not confirm:
            return

        success, message = create_sale(
            customer_name,
            customer_address,
            serial_number,
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

    # =====================================================
    # CLEAR FORM
    # =====================================================

    def clear_form(self):
        self.customer_name_entry.delete(
            0,
            "end"
        )

        self.address_entry.delete(
            0,
            "end"
        )

        self.serial_entry.delete(
            0,
            "end"
        )

        self.quantity_entry.delete(
            0,
            "end"
        )

        self.profit_entry.delete(
            0,
            "end"
        )

        self.sale_items.clear()

        self.calculated_profit_label.configure(
            text="৳ 0.00"
        )

        self.refresh_items_table()

        self.customer_name_entry.focus()

    # =====================================================
    # CLOSE
    # =====================================================

    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()

