
import customtkinter as ctk

from config import APP_NAME, create_required_folders
from database import initialize_database
from ui.dashboard import Dashboard


def main():
    create_required_folders()
    initialize_database()

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()

