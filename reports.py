import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta

from database import (
    get_sales_report,
    get_sale_items,
    delete_sale
)


class ReportsWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.current_report_type = "today"
        self.current_sales = []

        self.title("Sales Reports")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        self.transient(parent)
        self.lift()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.create_ui()
        self.load_today_report()

    def create_ui(self):
        self.configure(fg_color="#F1F5F9")

        header = ctk.CTkFrame(
            self, height=70, corner_radius=0, fg_color="#1E293B"
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="Sales Reports",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=18)

        ctk.CTkButton(
            header,
            text="Close",
            width=100,
            height=38,
            command=self.close_window,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        ).pack(side="right", padx=25)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)

        filter_frame = ctk.CTkFrame(
            content, fg_color="white", corner_radius=12
        )
        filter_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            filter_frame,
            text="Report Period",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left", padx=20, pady=18)

        self.today_button = ctk.CTkButton(
            filter_frame, text="Today", width=110,
            command=self.load_today_report
        )
        self.today_button.pack(side="left", padx=5)

        self.month_button = ctk.CTkButton(
            filter_frame, text="This Month", width=120,
            command=self.load_monthly_report
        )
        self.month_button.pack(side="left", padx=5)

        self.year_button = ctk.CTkButton(
            filter_frame, text="This Year", width=110,
            command=self.load_yearly_report
        )
        self.year_button.pack(side="left", padx=5)

        self.all_button = ctk.CTkButton(
            filter_frame, text="All Sales", width=110,
            command=self.load_all_report
        )
        self.all_button.pack(side="left", padx=5)

        ctk.CTkButton(
            filter_frame,
            text="Refresh",
            width=100,
            command=self.refresh_current_report,
            fg_color="#0F766E",
            hover_color="#115E59"
        ).pack(side="right", padx=20)

        summary_frame = ctk.CTkFrame(content, fg_color="transparent")
        summary_frame.pack(fill="x", pady=(0, 15))

        for column in range(3):
            summary_frame.grid_columnconfigure(column, weight=1)

        self.total_sales_label = self.create_summary_card(
            summary_frame, 0, "TOTAL SALES", "#2563EB"
        )
        self.total_quantity_label = self.create_summary_card(
            summary_frame, 1, "TOTAL QUANTITY", "#7C3AED"
        )
        self.total_profit_label = self.create_summary_card(
            summary_frame, 2, "TOTAL PROFIT", "#059669"
        )

        search_frame = ctk.CTkFrame(
            content, fg_color="white", corner_radius=12
        )
        search_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            search_frame,
            text="Search Serial Number",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=(20, 10), pady=15)

        self.serial_search_entry = ctk.CTkEntry(
            search_frame,
            width=300,
            placeholder_text="Enter serial number..."
        )
        self.serial_search_entry.pack(side="left", padx=5, pady=15)
        self.serial_search_entry.bind(
            "<Return>", lambda event: self.search_by_serial()
        )

        ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=self.search_by_serial
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Clear",
            width=100,
            command=self.clear_serial_search,
            fg_color="#64748B",
            hover_color="#475569"
        ).pack(side="left", padx=5)

        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 8))

        self.report_title_label = ctk.CTkLabel(
            title_frame,
            text="Today's Sales Report",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#0F172A"
        )
        self.report_title_label.pack(side="left")

        ctk.CTkButton(
            title_frame,
            text="Delete Selected Sale",
            width=180,
            height=38,
            command=self.delete_selected_sale,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        ).pack(side="right")

        ctk.CTkLabel(
            title_frame,
            text="Double-click a sale to view details",
            font=ctk.CTkFont(size=12),
            text_color="#64748B"
        ).pack(side="right", padx=(0, 15))

        table_frame = ctk.CTkFrame(
            content, fg_color="white", corner_radius=12
        )
        table_frame.pack(fill="both", expand=True)

        self.create_sales_table(table_frame)

    def create_summary_card(self, parent, column, title, color):
        card = ctk.CTkFrame(
            parent,
            height=105,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=0, column=column, sticky="nsew", padx=6)
        card.grid_propagate(False)

        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#64748B"
        ).pack(pady=(18, 4))

        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=color
        )
        value_label.pack()
        return value_label

    def create_sales_table(self, parent):
        style = ttk.Style()
        style.configure("Treeview", rowheight=32, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

        columns = (
            "id", "customer", "address", "serial",
            "quantity", "profit", "date"
        )

        self.sales_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "Sale ID",
            "customer": "Customer Name",
            "address": "Address",
            "serial": "Serial Number",
            "quantity": "Quantity",
            "profit": "Profit",
            "date": "Date & Time"
        }

        for column, text in headings.items():
            self.sales_tree.heading(column, text=text)

        self.sales_tree.column("id", width=70, anchor="center")
        self.sales_tree.column("customer", width=170, anchor="w")
        self.sales_tree.column("address", width=190, anchor="w")
        self.sales_tree.column("serial", width=150, anchor="center")
        self.sales_tree.column("quantity", width=90, anchor="center")
        self.sales_tree.column("profit", width=110, anchor="center")
        self.sales_tree.column("date", width=170, anchor="center")

        vertical_scrollbar = ttk.Scrollbar(
            parent, orient="vertical", command=self.sales_tree.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            parent, orient="horizontal", command=self.sales_tree.xview
        )

        self.sales_tree.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )

        self.sales_tree.pack(
            side="top", fill="both", expand=True,
            padx=10, pady=(10, 0)
        )
        horizontal_scrollbar.pack(
            side="bottom", fill="x", padx=10, pady=(0, 10)
        )
        vertical_scrollbar.place(
            relx=0.985, rely=0.02, relheight=0.90
        )

        self.sales_tree.bind("<Double-1>", self.open_sale_details)

    def load_today_report(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.current_report_type = "today"
        self.report_title_label.configure(text="Today's Sales Report")
        self.load_report(today, today)

    def load_monthly_report(self):
        now = datetime.now()
        first_day = now.replace(day=1)

        if now.month == 12:
            next_month = now.replace(
                year=now.year + 1, month=1, day=1
            )
        else:
            next_month = now.replace(
                month=now.month + 1, day=1
            )

        last_day = next_month - timedelta(days=1)
        self.current_report_type = "month"
        self.report_title_label.configure(
            text="This Month's Sales Report"
        )
        self.load_report(
            first_day.strftime("%Y-%m-%d"),
            last_day.strftime("%Y-%m-%d")
        )

    def load_yearly_report(self):
        now = datetime.now()
        self.current_report_type = "year"
        self.report_title_label.configure(
            text="This Year's Sales Report"
        )
        self.load_report(
            f"{now.year}-01-01",
            f"{now.year}-12-31"
        )

    def load_all_report(self):
        self.current_report_type = "all"
        self.report_title_label.configure(text="All Sales Report")
        self.load_report()

    def load_report(self, start_date=None, end_date=None):
        try:
            self.current_sales = get_sales_report(
                start_date, end_date
            )

            for item in self.sales_tree.get_children():
                self.sales_tree.delete(item)

            total_quantity = 0
            total_profit = 0.0

            for sale in self.current_sales:
                self.sales_tree.insert(
                    "",
                    "end",
                    values=(
                        sale["id"],
                        sale["customer_name"],
                        sale["customer_address"] or "",
                        sale.get("serial_number", ""),
                        sale["total_quantity"],
                        f"৳ {float(sale['total_profit']):,.2f}",
                        sale["created_at"]
                    )
                )

                total_quantity += int(sale["total_quantity"])
                total_profit += float(sale["total_profit"])

            self.total_sales_label.configure(
                text=str(len(self.current_sales))
            )
            self.total_quantity_label.configure(
                text=str(total_quantity)
            )
            self.total_profit_label.configure(
                text=f"৳ {total_profit:,.2f}"
            )

        except Exception as error:
            messagebox.showerror(
                "Report Error", str(error), parent=self
            )

    def refresh_current_report(self):
        if self.current_report_type == "today":
            self.load_today_report()
        elif self.current_report_type == "month":
            self.load_monthly_report()
        elif self.current_report_type == "year":
            self.load_yearly_report()
        else:
            self.load_all_report()

    def search_by_serial(self):
        search_text = self.serial_search_entry.get().strip().lower()

        if not search_text:
            messagebox.showwarning(
                "Search",
                "Please enter a serial number.",
                parent=self
            )
            return

        try:
            matched_sales = []

            # Search inside sale_items because each category has its own serial number.
            for sale in self.current_sales:
                sale_id = int(sale["id"])
                items = get_sale_items(sale_id)

                matching_serials = []

                for item in items:
                    item_serial = str(
                        item.get("serial_number", "") or ""
                    ).strip()

                    if search_text in item_serial.lower():
                        matching_serials.append(item_serial)

                # Also support older sales that stored serial in the sales table.
                old_serial = str(
                    sale.get("serial_number", "") or ""
                ).strip()

                if search_text in old_serial.lower() and old_serial:
                    matching_serials.append(old_serial)

                if matching_serials:
                    matched_sales.append(
                        (sale, ", ".join(dict.fromkeys(matching_serials)))
                    )

            for row in self.sales_tree.get_children():
                self.sales_tree.delete(row)

            total_quantity = 0
            total_profit = 0.0

            for sale, matched_serials in matched_sales:
                self.sales_tree.insert(
                    "",
                    "end",
                    values=(
                        sale["id"],
                        sale["customer_name"],
                        sale["customer_address"] or "",
                        matched_serials,
                        sale["total_quantity"],
                        f"৳ {float(sale['total_profit']):,.2f}",
                        sale["created_at"]
                    )
                )

                total_quantity += int(sale["total_quantity"])
                total_profit += float(sale["total_profit"])

            self.total_sales_label.configure(
                text=str(len(matched_sales))
            )
            self.total_quantity_label.configure(
                text=str(total_quantity)
            )
            self.total_profit_label.configure(
                text=f"৳ {total_profit:,.2f}"
            )

            self.report_title_label.configure(
                text=f"Serial Search Result: {self.serial_search_entry.get().strip()}"
            )

            if not matched_sales:
                messagebox.showinfo(
                    "Search Result",
                    "No sale found with this serial number.",
                    parent=self
                )

        except Exception as error:
            messagebox.showerror(
                "Search Error", str(error), parent=self
            )

    def clear_serial_search(self):
        self.serial_search_entry.delete(0, "end")
        self.refresh_current_report()

    def delete_selected_sale(self):
        selected = self.sales_tree.selection()

        if not selected:
            messagebox.showwarning(
                "No Selection",
                "Please select a sale to delete.",
                parent=self
            )
            return

        values = self.sales_tree.item(selected[0], "values")
        if not values:
            return

        sale_id = int(values[0])
        customer_name = values[1]
        quantity = values[4]
        profit = values[5]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            (
                f"Are you sure you want to delete Sale #{sale_id}?\n\n"
                f"Customer: {customer_name}\n"
                f"Quantity: {quantity}\n"
                f"Profit: {profit}\n\n"
                "The sold stamp quantity will be restored to stock.\n"
                "This action cannot be undone."
            ),
            parent=self
        )

        if not confirm:
            return

        try:
            success, message = delete_sale(sale_id)

            if success:
                messagebox.showinfo(
                    "Sale Deleted", message, parent=self
                )
                self.refresh_current_report()

                # Refresh dashboard if the parent provides a refresh method.
                for method_name in (
                    "refresh_dashboard",
                    "refresh_data",
                    "load_dashboard_data",
                    "load_data"
                ):
                    method = getattr(self.parent, method_name, None)
                    if callable(method):
                        method()
                        break
            else:
                messagebox.showerror(
                    "Delete Error", message, parent=self
                )

        except Exception as error:
            messagebox.showerror(
                "Delete Error", str(error), parent=self
            )

    def open_sale_details(self, event=None):
        selected = self.sales_tree.selection()
        if not selected:
            return

        values = self.sales_tree.item(selected[0], "values")
        if not values:
            return

        sale_id = int(values[0])
        sale = None

        for current_sale in self.current_sales:
            if int(current_sale["id"]) == sale_id:
                sale = current_sale
                break

        if not sale:
            return

        try:
            items = get_sale_items(sale_id)
        except Exception as error:
            messagebox.showerror(
                "Details Error", str(error), parent=self
            )
            return

        self.show_details_window(sale, items)

    def show_details_window(self, sale, items):
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Sale Details - #{sale['id']}")
        details_window.geometry("850x580")
        details_window.minsize(700, 500)
        details_window.transient(self)
        details_window.lift()
        details_window.focus_force()

        header = ctk.CTkFrame(
            details_window,
            height=65,
            corner_radius=0,
            fg_color="#1E293B"
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text=f"Sale Details #{sale['id']}",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=25, pady=16)

        info_frame = ctk.CTkFrame(
            details_window, fg_color="white", corner_radius=12
        )
        info_frame.pack(fill="x", padx=20, pady=20)

        info_text = (
            f"Customer Name: {sale['customer_name']}\n"
            f"Address: {sale['customer_address'] or ''}\n"
            f"Date: {sale['created_at']}"
        )

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=14)
        ).pack(fill="x", padx=20, pady=18)

        items_frame = ctk.CTkFrame(
            details_window, fg_color="white", corner_radius=12
        )
        items_frame.pack(
            fill="both", expand=True, padx=20, pady=(0, 15)
        )

        columns = (
            "category", "serial", "quantity",
            "profit_each", "profit"
        )

        item_tree = ttk.Treeview(
            items_frame, columns=columns, show="headings"
        )

        item_tree.heading("category", text="Category")
        item_tree.heading("serial", text="Serial Number")
        item_tree.heading("quantity", text="Quantity")
        item_tree.heading("profit_each", text="Profit Per Stamp")
        item_tree.heading("profit", text="Total Profit")

        item_tree.column("category", anchor="center", width=150)
        item_tree.column("serial", anchor="center", width=200)
        item_tree.column("quantity", anchor="center", width=100)
        item_tree.column("profit_each", anchor="center", width=140)
        item_tree.column("profit", anchor="center", width=140)

        for item in items:
            quantity = int(item["quantity"])
            total_item_profit = float(item["profit"])
            profit_each = (
                total_item_profit / quantity if quantity else 0.0
            )

            item_tree.insert(
                "",
                "end",
                values=(
                    item["category_name"],
                    item.get("serial_number", ""),
                    quantity,
                    f"৳ {profit_each:,.2f}",
                    f"৳ {total_item_profit:,.2f}"
                )
            )

        item_tree.pack(
            fill="both", expand=True, padx=15, pady=15
        )

        total_frame = ctk.CTkFrame(
            details_window, fg_color="transparent"
        )
        total_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            total_frame,
            text=f"Total Quantity: {sale['total_quantity']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            total_frame,
            text=f"Total Profit: ৳ {float(sale['total_profit']):,.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#059669"
        ).pack(side="right")

    def close_window(self):
        self.destroy()
