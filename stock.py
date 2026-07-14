
import customtkinter as ctk
from tkinter import messagebox, ttk

from database import (
    get_categories,
    add_stock,
    get_stock_history
)


class StockWindow(ctk.CTkToplevel):

    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)

        self.parent = parent
        self.refresh_callback = refresh_callback
        self.categories = []
        self.category_map = {}

        self.title("Stock Management")
        self.geometry("1050x700")
        self.minsize(900, 600)

        self.transient(parent)
        self.lift()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.create_ui()
        self.load_categories()
        self.load_stock_history()

    # =====================================================
    # MAIN UI
    # =====================================================

    def create_ui(self):
        self.configure(fg_color="#F1F5F9")

        # HEADER
        header_frame = ctk.CTkFrame(
            self,
            height=75,
            corner_radius=0,
            fg_color="#1E293B"
        )
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="Stock Management",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            ),
            text_color="white"
        )
        title_label.pack(
            side="left",
            padx=30,
            pady=20
        )

        close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            width=100,
            height=38,
            command=self.close_window,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        close_button.pack(
            side="right",
            padx=25,
            pady=18
        )

        # CONTENT
        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=20
        )

        # ADD STOCK SECTION
        form_frame = ctk.CTkFrame(
            content_frame,
            fg_color="white",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0"
        )
        form_frame.pack(
            fill="x",
            pady=(0, 20)
        )

        form_title = ctk.CTkLabel(
            form_frame,
            text="Add New Stock",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color="#0F172A"
        )
        form_title.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="w",
            padx=25,
            pady=(20, 15)
        )

        # CATEGORY
        category_label = ctk.CTkLabel(
            form_frame,
            text="Stamp Category",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color="#334155"
        )
        category_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=(25, 10),
            pady=5
        )

        self.category_combo = ctk.CTkComboBox(
            form_frame,
            values=["No Category"],
            width=220,
            height=40,
            state="readonly",
            command=self.on_category_change
        )
        self.category_combo.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=(25, 10),
            pady=(0, 20)
        )

        # QUANTITY
        quantity_label = ctk.CTkLabel(
            form_frame,
            text="Quantity",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color="#334155"
        )
        quantity_label.grid(
            row=1,
            column=1,
            sticky="w",
            padx=10,
            pady=5
        )

        self.quantity_entry = ctk.CTkEntry(
            form_frame,
            width=180,
            height=40,
            placeholder_text="Enter quantity"
        )
        self.quantity_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=10,
            pady=(0, 20)
        )

        # NOTE
        note_label = ctk.CTkLabel(
            form_frame,
            text="Note",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color="#334155"
        )
        note_label.grid(
            row=1,
            column=2,
            sticky="w",
            padx=10,
            pady=5
        )

        self.note_entry = ctk.CTkEntry(
            form_frame,
            width=260,
            height=40,
            placeholder_text="Optional note"
        )
        self.note_entry.grid(
            row=2,
            column=2,
            sticky="ew",
            padx=10,
            pady=(0, 20)
        )

        # ADD BUTTON
        self.add_button = ctk.CTkButton(
            form_frame,
            text="Add Stock",
            height=40,
            width=150,
            command=self.save_stock,
            fg_color="#059669",
            hover_color="#047857",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        )
        self.add_button.grid(
            row=2,
            column=3,
            padx=(10, 25),
            pady=(0, 20)
        )

        for column in range(3):
            form_frame.grid_columnconfigure(
                column,
                weight=1
            )

        # CURRENT STOCK INFO
        self.current_stock_label = ctk.CTkLabel(
            form_frame,
            text="Current Stock: 0",
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            text_color="#2563EB"
        )
        self.current_stock_label.grid(
            row=3,
            column=0,
            columnspan=4,
            sticky="w",
            padx=25,
            pady=(0, 20)
        )

        # HISTORY HEADER
        history_header = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        history_header.pack(
            fill="x",
            pady=(0, 10)
        )

        history_title = ctk.CTkLabel(
            history_header,
            text="Stock History",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color="#0F172A"
        )
        history_title.pack(side="left")

        refresh_button = ctk.CTkButton(
            history_header,
            text="Refresh",
            width=100,
            height=35,
            command=self.refresh_data
        )
        refresh_button.pack(side="right")

        # TABLE FRAME
        table_frame = ctk.CTkFrame(
            content_frame,
            fg_color="white",
            corner_radius=10
        )
        table_frame.pack(
            fill="both",
            expand=True
        )

        self.create_history_table(table_frame)

    # =====================================================
    # HISTORY TABLE
    # =====================================================

    def create_history_table(self, parent):
        style = ttk.Style()

        style.configure(
            "Treeview",
            rowheight=32,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold")
        )

        columns = (
            "id",
            "category",
            "quantity",
            "note",
            "date"
        )

        self.history_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings"
        )

        self.history_tree.heading(
            "id",
            text="ID"
        )
        self.history_tree.heading(
            "category",
            text="Category"
        )
        self.history_tree.heading(
            "quantity",
            text="Quantity Added"
        )
        self.history_tree.heading(
            "note",
            text="Note"
        )
        self.history_tree.heading(
            "date",
            text="Date & Time"
        )

        self.history_tree.column(
            "id",
            width=70,
            anchor="center"
        )
        self.history_tree.column(
            "category",
            width=160,
            anchor="center"
        )
        self.history_tree.column(
            "quantity",
            width=140,
            anchor="center"
        )
        self.history_tree.column(
            "note",
            width=300,
            anchor="w"
        )
        self.history_tree.column(
            "date",
            width=180,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.history_tree.yview
        )

        self.history_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.history_tree.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0),
            pady=10
        )

        scrollbar.pack(
            side="right",
            fill="y",
            padx=(0, 10),
            pady=10
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

            category_names = []

            for category in self.categories:
                name = str(category["name"])

                category_names.append(name)

                self.category_map[name] = category

            if category_names:
                self.category_combo.configure(
                    values=category_names
                )

                self.category_combo.set(
                    category_names[0]
                )

                self.update_current_stock()

            else:
                self.category_combo.configure(
                    values=["No Category"]
                )

                self.category_combo.set(
                    "No Category"
                )

                self.current_stock_label.configure(
                    text="Current Stock: 0"
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

    def on_category_change(self, selected_value):
        self.update_current_stock()

    def update_current_stock(self):
        selected_name = self.category_combo.get()

        category = self.category_map.get(
            selected_name
        )

        if category:
            stock = int(
                category["current_stock"]
            )

            self.current_stock_label.configure(
                text=f"Current Stock: {stock}"
            )

        else:
            self.current_stock_label.configure(
                text="Current Stock: 0"
            )

    # =====================================================
    # SAVE STOCK
    # =====================================================

    def save_stock(self):
        selected_name = self.category_combo.get()

        category = self.category_map.get(
            selected_name
        )

        if not category:
            messagebox.showwarning(
                "Select Category",
                "Please select a valid stamp category.",
                parent=self
            )
            return

        quantity_text = self.quantity_entry.get().strip()

        if not quantity_text:
            messagebox.showwarning(
                "Quantity Required",
                "Please enter stock quantity.",
                parent=self
            )
            self.quantity_entry.focus()
            return

        try:
            quantity = int(quantity_text)

        except ValueError:
            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be a whole number.",
                parent=self
            )
            self.quantity_entry.focus()
            return

        if quantity <= 0:
            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be greater than 0.",
                parent=self
            )
            return

        note = self.note_entry.get().strip()

        confirm = messagebox.askyesno(
            "Confirm Stock",
            (
                f"Category: {selected_name}\n"
                f"Quantity: {quantity}\n\n"
                "Do you want to add this stock?"
            ),
            parent=self
        )

        if not confirm:
            return

        success, message = add_stock(
            category["id"],
            quantity,
            note
        )

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=self
            )

            self.quantity_entry.delete(
                0,
                "end"
            )

            self.note_entry.delete(
                0,
                "end"
            )

            self.refresh_data()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Stock Error",
                message,
                parent=self
            )

    # =====================================================
    # LOAD STOCK HISTORY
    # =====================================================

    def load_stock_history(self):
        try:
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            history = get_stock_history()

            for row in history:
                self.history_tree.insert(
                    "",
                    "end",
                    values=(
                        row["id"],
                        row["category_name"],
                        row["quantity_added"],
                        row["note"] or "",
                        row["created_at"]
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "History Error",
                str(error),
                parent=self
            )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh_data(self):
        self.load_categories()
        self.load_stock_history()

        if self.refresh_callback:
            self.refresh_callback()

    # =====================================================
    # CLOSE WINDOW
    # =====================================================

    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()

