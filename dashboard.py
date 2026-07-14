
import customtkinter as ctk
from tkinter import messagebox

from config import APP_NAME
from database import get_dashboard_data


class Dashboard(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1250x750")
        self.minsize(1050, 650)

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_area()
        self.refresh_dashboard()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color="#1E293B"
        )
        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        self.sidebar.grid_propagate(False)

        title = ctk.CTkLabel(
            self.sidebar,
            text="STAMP SALES",
            font=ctk.CTkFont(size=23, weight="bold"),
            text_color="white"
        )
        title.pack(pady=(35, 5), padx=15)

        subtitle = ctk.CTkLabel(
            self.sidebar,
            text="Management Software",
            font=ctk.CTkFont(size=13),
            text_color="#CBD5E1"
        )
        subtitle.pack(pady=(0, 35))

        self.create_menu_button(
            "Dashboard",
            self.refresh_dashboard
        )

        self.create_menu_button(
            "New Sale",
            self.open_sales
        )

        self.create_menu_button(
            "Stock Management",
            self.open_stock
        )

        self.create_menu_button(
            "Categories",
            self.open_categories
        )

        self.create_menu_button(
            "Reports",
            self.open_reports
        )

        refresh_button = ctk.CTkButton(
            self.sidebar,
            text="Refresh Dashboard",
            command=self.refresh_dashboard,
            height=42,
            fg_color="#0F766E",
            hover_color="#115E59"
        )
        refresh_button.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

    def create_menu_button(self, text, command):
        button = ctk.CTkButton(
            self.sidebar,
            text=text,
            command=command,
            height=45,
            corner_radius=7,
            anchor="w",
            fg_color="transparent",
            hover_color="#334155",
            text_color="white",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        button.pack(
            fill="x",
            padx=15,
            pady=5
        )

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#F1F5F9"
        )
        self.main_frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        header_frame.pack(
            fill="x",
            padx=30,
            pady=(25, 10)
        )

        heading = ctk.CTkLabel(
            header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#0F172A"
        )
        heading.pack(side="left")

        self.status_label = ctk.CTkLabel(
            header_frame,
            text="Ready",
            font=ctk.CTkFont(size=13),
            text_color="#64748B"
        )
        self.status_label.pack(side="right")

        self.profit_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.profit_frame.pack(
            fill="x",
            padx=25,
            pady=10
        )

        for column in range(3):
            self.profit_frame.grid_columnconfigure(
                column,
                weight=1
            )

        self.today_profit_value = self.create_profit_card(
            self.profit_frame,
            0,
            "TODAY PROFIT",
            "#2563EB"
        )

        self.monthly_profit_value = self.create_profit_card(
            self.profit_frame,
            1,
            "MONTHLY PROFIT",
            "#059669"
        )

        self.yearly_profit_value = self.create_profit_card(
            self.profit_frame,
            2,
            "YEARLY PROFIT",
            "#7C3AED"
        )

        stock_header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        stock_header.pack(
            fill="x",
            padx=30,
            pady=(20, 5)
        )

        stock_title = ctk.CTkLabel(
            stock_header,
            text="Current Stamp Stock",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#0F172A"
        )
        stock_title.pack(side="left")

        self.total_stock_label = ctk.CTkLabel(
            stock_header,
            text="Total Stock: 0",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#475569"
        )
        self.total_stock_label.pack(side="right")

        self.stock_scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent"
        )
        self.stock_scroll_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(5, 25)
        )

    def create_profit_card(
        self,
        parent,
        column,
        title,
        color
    ):
        card = ctk.CTkFrame(
            parent,
            height=130,
            corner_radius=12,
            fg_color="white",
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=7
        )
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#64748B"
        )
        title_label.pack(pady=(25, 5))

        value_label = ctk.CTkLabel(
            card,
            text="৳ 0.00",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=5)

        return value_label

    def create_stock_cards(self, categories):
        for widget in self.stock_scroll_frame.winfo_children():
            widget.destroy()

        columns = 4

        for column in range(columns):
            self.stock_scroll_frame.grid_columnconfigure(
                column,
                weight=1
            )

        total_stock = 0

        for index, category in enumerate(categories):
            row = index // columns
            column = index % columns

            category_name = category["name"]
            stock = int(category["current_stock"])

            total_stock += stock

            if stock <= 0:
                stock_color = "#DC2626"
                status_text = "Out of Stock"

            elif stock <= 10:
                stock_color = "#D97706"
                status_text = "Low Stock"

            else:
                stock_color = "#059669"
                status_text = "Available"

            card = ctk.CTkFrame(
                self.stock_scroll_frame,
                height=150,
                corner_radius=12,
                fg_color="white",
                border_width=1,
                border_color="#E2E8F0"
            )
            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=8,
                pady=8
            )
            card.grid_propagate(False)

            name_label = ctk.CTkLabel(
                card,
                text=category_name,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#0F172A"
            )
            name_label.pack(pady=(20, 5))

            stock_label = ctk.CTkLabel(
                card,
                text=str(stock),
                font=ctk.CTkFont(size=34, weight="bold"),
                text_color=stock_color
            )
            stock_label.pack(pady=3)

            status_label = ctk.CTkLabel(
                card,
                text=status_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=stock_color
            )
            status_label.pack(pady=3)

        self.total_stock_label.configure(
            text=f"Total Stock: {total_stock}"
        )

    def refresh_dashboard(self):
        try:
            data = get_dashboard_data()

            self.today_profit_value.configure(
                text=f"৳ {data['today_profit']:,.2f}"
            )

            self.monthly_profit_value.configure(
                text=f"৳ {data['monthly_profit']:,.2f}"
            )

            self.yearly_profit_value.configure(
                text=f"৳ {data['yearly_profit']:,.2f}"
            )

            self.create_stock_cards(
                data["categories"]
            )

            self.status_label.configure(
                text="Dashboard Updated"
            )

        except Exception as error:
            messagebox.showerror(
                "Dashboard Error",
                str(error)
            )

    def open_sales(self):
        try:
            from ui.sales import SalesWindow

            window = SalesWindow(
                self,
                refresh_callback=self.refresh_dashboard
            )
            window.lift()
            window.focus_force()

        except ImportError:
            messagebox.showinfo(
                "New Sale",
                "ui/sales.py will be added next."
            )

    def open_stock(self):
        try:
            from ui.stock import StockWindow

            window = StockWindow(
                self,
                refresh_callback=self.refresh_dashboard
            )
            window.lift()
            window.focus_force()

        except ImportError:
            messagebox.showinfo(
                "Stock Management",
                "ui/stock.py will be added next."
            )

    def open_categories(self):
        try:
            from ui.categories import CategoriesWindow

            window = CategoriesWindow(
                self,
                refresh_callback=self.refresh_dashboard
            )
            window.lift()
            window.focus_force()

        except ImportError:
            messagebox.showinfo(
                "Categories",
                "ui/categories.py will be added next."
            )

    def open_reports(self):
        try:
            from ui.reports import ReportsWindow

            window = ReportsWindow(self)
            window.lift()
            window.focus_force()

        except ImportError:
            messagebox.showinfo(
                "Reports",
                "ui/reports.py will be added next."
            )

    def close_app(self):
        self.destroy()

