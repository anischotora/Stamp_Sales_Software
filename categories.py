
import customtkinter as ctk
from tkinter import messagebox, ttk

from database import (
    get_categories,
    add_category,
    update_category,
    set_category_status
)


class CategoriesWindow(ctk.CTkToplevel):

    def __init__(self, parent, refresh_callback=None):
        super().__init__(parent)

        self.parent = parent
        self.refresh_callback = refresh_callback
        self.selected_category_id = None

        self.title("Stamp Categories")
        self.geometry("900x650")
        self.minsize(800, 550)

        self.transient(parent)
        self.lift()
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.create_ui()
        self.load_categories()

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
            text="Stamp Category Management",
            font=ctk.CTkFont(
                size=25,
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

        # MAIN CONTENT
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

        # FORM
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
            text="Add / Edit Category",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color="#0F172A"
        )
        form_title.pack(
            anchor="w",
            padx=25,
            pady=(20, 10)
        )

        input_frame = ctk.CTkFrame(
            form_frame,
            fg_color="transparent"
        )
        input_frame.pack(
            fill="x",
            padx=25,
            pady=(5, 20)
        )

        self.category_entry = ctk.CTkEntry(
            input_frame,
            height=42,
            placeholder_text="Enter category name, e.g. 200"
        )
        self.category_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.add_button = ctk.CTkButton(
            input_frame,
            text="Add Category",
            width=130,
            height=42,
            command=self.save_new_category,
            fg_color="#059669",
            hover_color="#047857"
        )
        self.add_button.pack(
            side="left",
            padx=5
        )

        self.update_button = ctk.CTkButton(
            input_frame,
            text="Update",
            width=110,
            height=42,
            command=self.save_category_update,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            state="disabled"
        )
        self.update_button.pack(
            side="left",
            padx=5
        )

        self.clear_button = ctk.CTkButton(
            input_frame,
            text="Clear",
            width=90,
            height=42,
            command=self.clear_selection,
            fg_color="#64748B",
            hover_color="#475569"
        )
        self.clear_button.pack(
            side="left",
            padx=(5, 0)
        )

        # TABLE HEADER
        table_header = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        table_header.pack(
            fill="x",
            pady=(0, 10)
        )

        list_title = ctk.CTkLabel(
            table_header,
            text="All Stamp Categories",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color="#0F172A"
        )
        list_title.pack(side="left")

        refresh_button = ctk.CTkButton(
            table_header,
            text="Refresh",
            width=100,
            height=35,
            command=self.load_categories
        )
        refresh_button.pack(side="right")

        # TABLE
        table_frame = ctk.CTkFrame(
            content_frame,
            fg_color="white",
            corner_radius=10
        )
        table_frame.pack(
            fill="both",
            expand=True
        )

        self.create_table(table_frame)

        # ACTION BUTTONS
        action_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        action_frame.pack(
            fill="x",
            pady=(15, 0)
        )

        edit_button = ctk.CTkButton(
            action_frame,
            text="Edit Selected",
            width=140,
            height=40,
            command=self.edit_selected,
            fg_color="#2563EB",
            hover_color="#1D4ED8"
        )
        edit_button.pack(
            side="left",
            padx=(0, 8)
        )

        deactivate_button = ctk.CTkButton(
            action_frame,
            text="Deactivate",
            width=130,
            height=40,
            command=self.deactivate_selected,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        deactivate_button.pack(
            side="left",
            padx=8
        )

        activate_button = ctk.CTkButton(
            action_frame,
            text="Activate",
            width=130,
            height=40,
            command=self.activate_selected,
            fg_color="#059669",
            hover_color="#047857"
        )
        activate_button.pack(
            side="left",
            padx=8
        )

    # =====================================================
    # TABLE
    # =====================================================

    def create_table(self, parent):
        style = ttk.Style()

        style.configure(
            "Treeview",
            rowheight=34,
            font=("Arial", 11)
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 11, "bold")
        )

        columns = (
            "id",
            "name",
            "stock",
            "status",
            "created_at"
        )

        self.category_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        self.category_tree.heading(
            "id",
            text="ID"
        )

        self.category_tree.heading(
            "name",
            text="Category"
        )

        self.category_tree.heading(
            "stock",
            text="Current Stock"
        )

        self.category_tree.heading(
            "status",
            text="Status"
        )

        self.category_tree.heading(
            "created_at",
            text="Created Date"
        )

        self.category_tree.column(
            "id",
            width=70,
            anchor="center"
        )

        self.category_tree.column(
            "name",
            width=200,
            anchor="center"
        )

        self.category_tree.column(
            "stock",
            width=140,
            anchor="center"
        )

        self.category_tree.column(
            "status",
            width=120,
            anchor="center"
        )

        self.category_tree.column(
            "created_at",
            width=200,
            anchor="center"
        )

        scrollbar = ttk.Scrollbar(
            parent,
            orient="vertical",
            command=self.category_tree.yview
        )

        self.category_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.category_tree.pack(
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

        self.category_tree.bind(
            "<Double-1>",
            self.on_double_click
        )

    # =====================================================
    # LOAD CATEGORIES
    # =====================================================

    def load_categories(self):
        try:
            for item in self.category_tree.get_children():
                self.category_tree.delete(item)

            categories = get_categories(
                active_only=False
            )

            for category in categories:

                if int(category["is_active"]) == 1:
                    status = "Active"
                else:
                    status = "Inactive"

                self.category_tree.insert(
                    "",
                    "end",
                    values=(
                        category["id"],
                        category["name"],
                        category["current_stock"],
                        status,
                        category["created_at"]
                    )
                )

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                str(error),
                parent=self
            )

    # =====================================================
    # ADD CATEGORY
    # =====================================================

    def save_new_category(self):
        category_name = self.category_entry.get().strip()

        if not category_name:
            messagebox.showwarning(
                "Category Required",
                "Please enter a category name.",
                parent=self
            )
            self.category_entry.focus()
            return

        success, message = add_category(
            category_name
        )

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=self
            )

            self.category_entry.delete(
                0,
                "end"
            )

            self.load_categories()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Category Error",
                message,
                parent=self
            )

    # =====================================================
    # SELECTED CATEGORY
    # =====================================================

    def get_selected_category(self):
        selected_items = self.category_tree.selection()

        if not selected_items:
            messagebox.showwarning(
                "No Selection",
                "Please select a category first.",
                parent=self
            )
            return None

        selected_item = selected_items[0]

        values = self.category_tree.item(
            selected_item,
            "values"
        )

        if not values:
            return None

        return {
            "id": int(values[0]),
            "name": values[1],
            "stock": int(values[2]),
            "status": values[3],
            "created_at": values[4]
        }

    # =====================================================
    # EDIT CATEGORY
    # =====================================================

    def edit_selected(self):
        category = self.get_selected_category()

        if not category:
            return

        self.selected_category_id = category["id"]

        self.category_entry.delete(
            0,
            "end"
        )

        self.category_entry.insert(
            0,
            category["name"]
        )

        self.add_button.configure(
            state="disabled"
        )

        self.update_button.configure(
            state="normal"
        )

        self.category_entry.focus()

    def on_double_click(self, event):
        self.edit_selected()

    # =====================================================
    # UPDATE CATEGORY
    # =====================================================

    def save_category_update(self):
        if self.selected_category_id is None:
            messagebox.showwarning(
                "No Category",
                "Please select a category to update.",
                parent=self
            )
            return

        new_name = self.category_entry.get().strip()

        if not new_name:
            messagebox.showwarning(
                "Category Required",
                "Please enter a category name.",
                parent=self
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Update",
            "Do you want to update this category?",
            parent=self
        )

        if not confirm:
            return

        success, message = update_category(
            self.selected_category_id,
            new_name
        )

        if success:
            messagebox.showinfo(
                "Success",
                message,
                parent=self
            )

            self.clear_selection()
            self.load_categories()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Update Error",
                message,
                parent=self
            )

    # =====================================================
    # DEACTIVATE CATEGORY
    # =====================================================

    def deactivate_selected(self):
        category = self.get_selected_category()

        if not category:
            return

        if category["status"] == "Inactive":
            messagebox.showinfo(
                "Already Inactive",
                "This category is already inactive.",
                parent=self
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivate",
            (
                f"Do you want to deactivate "
                f"'{category['name']}'?"
            ),
            parent=self
        )

        if not confirm:
            return

        success = set_category_status(
            category["id"],
            False
        )

        if success:
            messagebox.showinfo(
                "Success",
                "Category deactivated successfully.",
                parent=self
            )

            self.clear_selection()
            self.load_categories()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Error",
                "Category could not be deactivated.",
                parent=self
            )

    # =====================================================
    # ACTIVATE CATEGORY
    # =====================================================

    def activate_selected(self):
        category = self.get_selected_category()

        if not category:
            return

        if category["status"] == "Active":
            messagebox.showinfo(
                "Already Active",
                "This category is already active.",
                parent=self
            )
            return

        success = set_category_status(
            category["id"],
            True
        )

        if success:
            messagebox.showinfo(
                "Success",
                "Category activated successfully.",
                parent=self
            )

            self.clear_selection()
            self.load_categories()

            if self.refresh_callback:
                self.refresh_callback()

        else:
            messagebox.showerror(
                "Error",
                "Category could not be activated.",
                parent=self
            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_selection(self):
        self.selected_category_id = None

        self.category_entry.delete(
            0,
            "end"
        )

        self.add_button.configure(
            state="normal"
        )

        self.update_button.configure(
            state="disabled"
        )

        for item in self.category_tree.selection():
            self.category_tree.selection_remove(item)

    # =====================================================
    # CLOSE WINDOW
    # =====================================================

    def close_window(self):
        if self.refresh_callback:
            self.refresh_callback()

        self.destroy()

