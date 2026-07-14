import sqlite3
from datetime import datetime

from config import DATABASE_PATH, create_required_folders


def get_connection():
    create_required_folders()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]
    return column_name in columns


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
            serial_number TEXT,
            total_quantity INTEGER NOT NULL DEFAULT 0,
            total_stamp_price REAL NOT NULL DEFAULT 0,
            total_profit REAL NOT NULL DEFAULT 0,
            grand_total REAL NOT NULL DEFAULT 0,
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
            serial_number TEXT,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL DEFAULT 0,
            stamp_price REAL NOT NULL DEFAULT 0,
            profit_per_stamp REAL NOT NULL DEFAULT 0,
            profit REAL NOT NULL DEFAULT 0,
            grand_total REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (sale_id)
                REFERENCES sales(id)
                ON DELETE CASCADE,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
    """)

    # =====================================================
    # UPGRADE OLD SALES TABLE
    # =====================================================

    sales_upgrades = {
        "serial_number": "TEXT",
        "total_stamp_price": "REAL NOT NULL DEFAULT 0",
        "grand_total": "REAL NOT NULL DEFAULT 0"
    }

    for column_name, column_definition in sales_upgrades.items():
        if not column_exists(
            cursor,
            "sales",
            column_name
        ):
            cursor.execute(
                f"""
                ALTER TABLE sales
                ADD COLUMN {column_name} {column_definition}
                """
            )

    # =====================================================
    # UPGRADE OLD SALE_ITEMS TABLE
    # =====================================================

    sale_items_upgrades = {
        "serial_number": "TEXT",
        "unit_price": "REAL NOT NULL DEFAULT 0",
        "stamp_price": "REAL NOT NULL DEFAULT 0",
        "profit_per_stamp": "REAL NOT NULL DEFAULT 0",
        "grand_total": "REAL NOT NULL DEFAULT 0"
    }

    for column_name, column_definition in sale_items_upgrades.items():
        if not column_exists(
            cursor,
            "sale_items",
            column_name
        ):
            cursor.execute(
                f"""
                ALTER TABLE sale_items
                ADD COLUMN {column_name} {column_definition}
                """
            )

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

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

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
        """, (
            category_name,
            now
        ))

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

    return [
        dict(row)
        for row in rows
    ]


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
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
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
        """, (
            name,
            category_id
        ))

        connection.commit()

        if cursor.rowcount == 0:
            return False, "Category not found."

        return True, "Category updated successfully."

    except sqlite3.IntegrityError:
        return False, "This category already exists."

    finally:
        connection.close()


def set_category_status(
    category_id,
    is_active
):
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

def add_stock(
    category_id,
    quantity,
    note=""
):
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
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
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

    return [
        dict(row)
        for row in rows
    ]


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
    Supports:
        create_sale(name, address, sale_items)

    Also keeps compatibility with:
        create_sale(name, address, serial, sale_items)
    """

    if (
        sale_items is None
        and isinstance(serial_number, (list, tuple))
    ):
        sale_items = serial_number
        serial_number = ""

    customer_name = str(
        customer_name
    ).strip()

    customer_address = str(
        customer_address or ""
    ).strip()

    serial_number = str(
        serial_number or ""
    ).strip()

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
        total_stamp_price = 0.0
        total_profit = 0.0
        grand_total = 0.0

        checked_items = []
        required_stock = {}

        for item in sale_items:
            category_id = int(
                item["category_id"]
            )

            quantity = int(
                item["quantity"]
            )

            item_serial = str(
                item.get(
                    "serial_number",
                    serial_number
                ) or ""
            ).strip()

            if quantity <= 0:
                connection.rollback()
                return (
                    False,
                    "Quantity must be greater than 0."
                )

            if not item_serial:
                connection.rollback()
                return (
                    False,
                    "Serial number is required for every category."
                )

            cursor.execute("""
                SELECT
                    id,
                    name,
                    current_stock
                FROM categories
                WHERE id = ?
                AND is_active = 1
            """, (category_id,))

            category = cursor.fetchone()

            if not category:
                connection.rollback()
                return (
                    False,
                    "One of the selected categories was not found."
                )

            try:
                unit_price = float(
                    item.get(
                        "unit_price",
                        category["name"]
                    )
                )
            except (ValueError, TypeError):
                unit_price = 0.0

            # Stamp face value
            stamp_price = (
                unit_price *
                quantity
            )

            # Profit entered in sales.py is per stamp.
            if "profit_per_stamp" in item:
                profit_per_stamp = float(
                    item.get(
                        "profit_per_stamp",
                        0
                    )
                )

                total_item_profit = (
                    profit_per_stamp *
                    quantity
                )
            else:
                # Compatibility with older sales.py
                total_item_profit = float(
                    item.get("profit", 0)
                )

                profit_per_stamp = (
                    total_item_profit / quantity
                    if quantity
                    else 0.0
                )

            if profit_per_stamp < 0:
                connection.rollback()
                return (
                    False,
                    "Profit cannot be negative."
                )

            item_grand_total = (
                stamp_price +
                total_item_profit
            )

            required_stock[category_id] = (
                required_stock.get(
                    category_id,
                    0
                )
                + quantity
            )

            checked_items.append({
                "category_id":
                    category["id"],

                "category_name":
                    category["name"],

                "serial_number":
                    item_serial,

                "quantity":
                    quantity,

                "unit_price":
                    unit_price,

                "stamp_price":
                    stamp_price,

                "profit_per_stamp":
                    profit_per_stamp,

                "profit":
                    total_item_profit,

                "grand_total":
                    item_grand_total
            })

            total_quantity += quantity
            total_stamp_price += stamp_price
            total_profit += total_item_profit
            grand_total += item_grand_total

        # =====================================================
        # CHECK STOCK
        # =====================================================

        for (
            category_id,
            required_quantity
        ) in required_stock.items():

            cursor.execute("""
                SELECT
                    name,
                    current_stock
                FROM categories
                WHERE id = ?
            """, (category_id,))

            category = cursor.fetchone()

            if not category:
                connection.rollback()
                return False, "Category not found."

            if (
                int(category["current_stock"])
                < required_quantity
            ):
                connection.rollback()

                return (
                    False,
                    (
                        f"Not enough stock for "
                        f"{category['name']}. "
                        f"Available stock: "
                        f"{category['current_stock']}"
                    )
                )

        now = datetime.now()

        sale_date = now.strftime(
            "%Y-%m-%d"
        )

        created_at = now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        header_serial = (
            serial_number
            or checked_items[0]["serial_number"]
        )

        cursor.execute("""
            INSERT INTO sales
            (
                customer_name,
                customer_address,
                serial_number,
                total_quantity,
                total_stamp_price,
                total_profit,
                grand_total,
                sale_date,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_name,
            customer_address,
            header_serial,
            total_quantity,
            total_stamp_price,
            total_profit,
            grand_total,
            sale_date,
            created_at
        ))

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
                    unit_price,
                    stamp_price,
                    profit_per_stamp,
                    profit,
                    grand_total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_id,
                item["category_id"],
                item["category_name"],
                item["serial_number"],
                item["quantity"],
                item["unit_price"],
                item["stamp_price"],
                item["profit_per_stamp"],
                item["profit"],
                item["grand_total"]
            ))

            cursor.execute("""
                UPDATE categories
                SET current_stock =
                    current_stock - ?
                WHERE id = ?
            """, (
                item["quantity"],
                item["category_id"]
            ))

        connection.commit()

        return (
            True,
            f"Sale saved successfully. Sale ID: {sale_id}"
        )

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

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    current_month = datetime.now().strftime(
        "%Y-%m"
    )

    current_year = datetime.now().strftime(
        "%Y"
    )

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(total_profit),
                0
            ) AS today_profit
        FROM sales
        WHERE sale_date = ?
    """, (today,))

    today_profit = cursor.fetchone()[
        "today_profit"
    ]

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(total_profit),
                0
            ) AS monthly_profit
        FROM sales
        WHERE substr(sale_date, 1, 7) = ?
    """, (current_month,))

    monthly_profit = cursor.fetchone()[
        "monthly_profit"
    ]

    cursor.execute("""
        SELECT
            COALESCE(
                SUM(total_profit),
                0
            ) AS yearly_profit
        FROM sales
        WHERE substr(sale_date, 1, 4) = ?
    """, (current_year,))

    yearly_profit = cursor.fetchone()[
        "yearly_profit"
    ]

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
        "today_profit":
            float(today_profit or 0),

        "monthly_profit":
            float(monthly_profit or 0),

        "yearly_profit":
            float(yearly_profit or 0),

        "categories":
            categories
    }


# =========================================================
# REPORT FUNCTIONS
# =========================================================

def get_sales_report(
    start_date=None,
    end_date=None
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM sales
        WHERE 1 = 1
    """

    parameters = []

    if start_date:
        query += """
            AND sale_date >= ?
        """
        parameters.append(start_date)

    if end_date:
        query += """
            AND sale_date <= ?
        """
        parameters.append(end_date)

    query += """
        ORDER BY id DESC
    """

    cursor.execute(
        query,
        parameters
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        dict(row)
        for row in rows
    ]


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

    return [
        dict(row)
        for row in rows
    ]


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
            SELECT
                category_id,
                quantity
            FROM sale_items
            WHERE sale_id = ?
        """, (sale_id,))

        items = cursor.fetchall()

        for item in items:
            cursor.execute("""
                UPDATE categories
                SET current_stock =
                    current_stock + ?
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

        return (
            True,
            (
                "Sale deleted successfully. "
                "Sold stock has been restored."
            )
        )

    except Exception as error:
        connection.rollback()
        return False, str(error)

    finally:
        connection.close()


initialize_database()
