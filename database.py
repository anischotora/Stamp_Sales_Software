
import sqlite3
from datetime import datetime

from config import DATABASE_PATH, create_required_folders


def get_connection():
    create_required_folders()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            current_stock INTEGER NOT NULL DEFAULT 0,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            customer_address TEXT,
            serial_number TEXT NOT NULL,
            total_quantity INTEGER NOT NULL DEFAULT 0,
            total_profit REAL NOT NULL DEFAULT 0,
            sale_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            profit REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (sale_id)
                REFERENCES sales(id)
                ON DELETE CASCADE,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
    """)

    # Upgrade older database: add serial_number to sale_items if missing.
    cursor.execute("PRAGMA table_info(sale_items)")
    sale_item_columns = [row["name"] for row in cursor.fetchall()]
    if "serial_number" not in sale_item_columns:
        cursor.execute("""
            ALTER TABLE sale_items
            ADD COLUMN serial_number TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            category_name TEXT NOT NULL,
            quantity_added INTEGER NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
    """)

    default_categories = [
        "100",
        "50",
        "30",
        "25",
        "20",
        "10",
        "5",
        "কাটিজ পেপার"
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for category_name in default_categories:
        cursor.execute("""
            INSERT OR IGNORE INTO categories
            (
                name,
                current_stock,
                is_active,
                created_at
            )
            VALUES (?, 0, 1, ?)
        """, (category_name, now))

    connection.commit()
    connection.close()


# =========================================================
# CATEGORY FUNCTIONS
# =========================================================

def get_categories(active_only=True):
    connection = get_connection()
    cursor = connection.cursor()

    if active_only:
        cursor.execute("""
            SELECT *
            FROM categories
            WHERE is_active = 1
            ORDER BY id ASC
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM categories
            ORDER BY id ASC
        """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_category(category_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM categories
        WHERE id = ?
    """, (category_id,))

    row = cursor.fetchone()
    connection.close()

    if row:
        return dict(row)

    return None


def add_category(name):
    name = name.strip()

    if not name:
        return False, "Category name is required."

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO categories
            (
                name,
                current_stock,
                is_active,
                created_at
            )
            VALUES (?, 0, 1, ?)
        """, (
            name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        return True, "Category added successfully."

    except sqlite3.IntegrityError:
        return False, "This category already exists."

    finally:
        connection.close()


def update_category(category_id, name):
    name = name.strip()

    if not name:
        return False, "Category name is required."

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE categories
            SET name = ?
            WHERE id = ?
        """, (name, category_id))

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Category not found."

        return True, "Category updated successfully."

    except sqlite3.IntegrityError:
        return False, "This category already exists."

    finally:
        connection.close()


def set_category_status(category_id, is_active):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE categories
        SET is_active = ?
        WHERE id = ?
    """, (
        1 if is_active else 0,
        category_id
    ))

    connection.commit()
    success = cursor.rowcount > 0
    connection.close()

    return success


# =========================================================
# STOCK FUNCTIONS
# =========================================================

def add_stock(category_id, quantity, note=""):
    quantity = int(quantity)

    if quantity <= 0:
        return False, "Quantity must be greater than 0."

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN")

        cursor.execute("""
            SELECT name
            FROM categories
            WHERE id = ?
        """, (category_id,))

        category = cursor.fetchone()

        if not category:
            connection.rollback()
            return False, "Category not found."

        category_name = category["name"]

        cursor.execute("""
            UPDATE categories
            SET current_stock = current_stock + ?
            WHERE id = ?
        """, (
            quantity,
            category_id
        ))

        cursor.execute("""
            INSERT INTO stock_history
            (
                category_id,
                category_name,
                quantity_added,
                note,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            category_id,
            category_name,
            quantity,
            note.strip(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        connection.commit()
        return True, "Stock added successfully."

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


def get_stock_history():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM stock_history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


# =========================================================
# SALES FUNCTIONS
# =========================================================

def create_sale(
    customer_name,
    customer_address,
    serial_number=None,
    sale_items=None
):
    """
    Supports both:
        create_sale(name, address, sale_items)
        create_sale(name, address, old_serial_number, sale_items)
    """

    # New sales.py calls: create_sale(name, address, sale_items)
    if sale_items is None and isinstance(serial_number, (list, tuple)):
        sale_items = serial_number
        serial_number = ""

    customer_name = str(customer_name).strip()
    customer_address = str(customer_address or "").strip()
    serial_number = str(serial_number or "").strip()
    sale_items = sale_items or []

    if not customer_name:
        return False, "Customer name is required."

    if not sale_items:
        return False, "At least one stamp item is required."

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN")

        total_quantity = 0
        total_profit = 0.0
        checked_items = []
        required_stock = {}

        for item in sale_items:
            category_id = int(item["category_id"])
            quantity = int(item["quantity"])
            profit = float(item.get("profit", 0))
            item_serial = str(
                item.get("serial_number", serial_number)
            ).strip()

            if quantity <= 0:
                return False, "Quantity must be greater than 0."

            if profit < 0:
                return False, "Profit cannot be negative."

            if not item_serial:
                return False, "Serial number is required for every category."

            cursor.execute("""
                SELECT id, name, current_stock
                FROM categories
                WHERE id = ? AND is_active = 1
            """, (category_id,))

            category = cursor.fetchone()

            if not category:
                connection.rollback()
                return False, "One of the selected categories was not found."

            required_stock[category_id] = (
                required_stock.get(category_id, 0) + quantity
            )

            checked_items.append({
                "category_id": category["id"],
                "category_name": category["name"],
                "serial_number": item_serial,
                "quantity": quantity,
                "profit": profit
            })

            total_quantity += quantity
            total_profit += profit

        # Check combined quantity when the same category is added more than once.
        for category_id, required_quantity in required_stock.items():
            cursor.execute("""
                SELECT name, current_stock
                FROM categories
                WHERE id = ?
            """, (category_id,))

            category = cursor.fetchone()

            if category["current_stock"] < required_quantity:
                connection.rollback()
                return (
                    False,
                    f"Not enough stock for {category['name']}. "
                    f"Available stock: {category['current_stock']}"
                )

        now = datetime.now()
        sale_date = now.strftime("%Y-%m-%d")
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")

        # Keep the old sales.serial_number column populated for compatibility.
        header_serial = serial_number or checked_items[0]["serial_number"]

        # Read the real sales table schema from the database currently in use.
        # This keeps the program compatible with older database files.
        cursor.execute("PRAGMA table_info(sales)")
        sales_columns = {
            row["name"]: row
            for row in cursor.fetchall()
        }

        sale_values = {
            "customer_name": customer_name,
            "customer_address": customer_address,
            "serial_number": header_serial,
            "total_quantity": total_quantity,
            "total_profit": total_profit,
            "sale_date": sale_date,
            "created_at": created_at
        }

        insert_columns = []
        insert_values = []

        for column_name, column_value in sale_values.items():
            if column_name in sales_columns:
                insert_columns.append(column_name)
                insert_values.append(column_value)

        placeholders = ", ".join(["?"] * len(insert_columns))
        column_sql = ", ".join(insert_columns)

        cursor.execute(
            f"INSERT INTO sales ({column_sql}) VALUES ({placeholders})",
            insert_values
        )

        sale_id = cursor.lastrowid

        for item in checked_items:
            cursor.execute("""
                INSERT INTO sale_items
                (
                    sale_id,
                    category_id,
                    category_name,
                    serial_number,
                    quantity,
                    profit
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["category_id"],
                item["category_name"],
                item["serial_number"],
                item["quantity"],
                item["profit"]
            ))

            cursor.execute("""
                UPDATE categories
                SET current_stock = current_stock - ?
                WHERE id = ?
            """, (
                item["quantity"],
                item["category_id"]
            ))

        connection.commit()
        return True, f"Sale saved successfully. Sale ID: {sale_id}"

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


# =========================================================
# DASHBOARD FUNCTIONS
# =========================================================

def get_dashboard_data():
    connection = get_connection()
    cursor = connection.cursor()

    today = datetime.now().strftime("%Y-%m-%d")
    current_month = datetime.now().strftime("%Y-%m")
    current_year = datetime.now().strftime("%Y")

    cursor.execute("""
        SELECT COALESCE(SUM(total_profit), 0)
        AS today_profit
        FROM sales
        WHERE sale_date = ?
    """, (today,))

    today_profit = cursor.fetchone()["today_profit"]

    cursor.execute("""
        SELECT COALESCE(SUM(total_profit), 0)
        AS monthly_profit
        FROM sales
        WHERE substr(sale_date, 1, 7) = ?
    """, (current_month,))

    monthly_profit = cursor.fetchone()["monthly_profit"]

    cursor.execute("""
        SELECT COALESCE(SUM(total_profit), 0)
        AS yearly_profit
        FROM sales
        WHERE substr(sale_date, 1, 4) = ?
    """, (current_year,))

    yearly_profit = cursor.fetchone()["yearly_profit"]

    cursor.execute("""
        SELECT *
        FROM categories
        WHERE is_active = 1
        ORDER BY id ASC
    """)

    categories = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return {
        "today_profit": float(today_profit),
        "monthly_profit": float(monthly_profit),
        "yearly_profit": float(yearly_profit),
        "categories": categories
    }


# =========================================================
# REPORT FUNCTIONS
# =========================================================

def get_sales_report(start_date=None, end_date=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM sales
        WHERE 1 = 1
    """

    parameters = []

    if start_date:
        query += " AND sale_date >= ?"
        parameters.append(start_date)

    if end_date:
        query += " AND sale_date <= ?"
        parameters.append(end_date)

    query += " ORDER BY id DESC"

    cursor.execute(query, parameters)

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]


def get_sale_items(sale_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM sale_items
        WHERE sale_id = ?
        ORDER BY id ASC
    """, (sale_id,))

    rows = cursor.fetchall()
    connection.close()

    return [dict(row) for row in rows]



# =========================================================
# DELETE SALE + RESTORE STOCK
# =========================================================

def delete_sale(sale_id):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("BEGIN")

        cursor.execute("""
            SELECT id
            FROM sales
            WHERE id = ?
        """, (sale_id,))

        if not cursor.fetchone():
            connection.rollback()
            return False, "Sale not found."

        cursor.execute("""
            SELECT category_id, quantity
            FROM sale_items
            WHERE sale_id = ?
        """, (sale_id,))

        items = cursor.fetchall()

        for item in items:
            cursor.execute("""
                UPDATE categories
                SET current_stock = current_stock + ?
                WHERE id = ?
            """, (
                item["quantity"],
                item["category_id"]
            ))

        cursor.execute("""
            DELETE FROM sale_items
            WHERE sale_id = ?
        """, (sale_id,))

        cursor.execute("""
            DELETE FROM sales
            WHERE id = ?
        """, (sale_id,))

        connection.commit()
        return True, "Sale deleted successfully. Sold stock has been restored."

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


# Ensure tables and migrations are ready whenever database.py is imported.
initialize_database()
