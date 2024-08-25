# gui/modules/data_management/fund_management.py

import tkinter as tk
from tkinter import ttk
from db.models import Fund
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy import create_engine


class FundManagement:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        self.engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Fund management UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for fund management."""
        title = tk.Label(self.frame, text="Fund Management", font=("Helvetica", 16))
        title.pack(pady=10)

        add_fund_button = tk.Button(self.frame, text="Add Fund", command=self.add_fund)
        add_fund_button.pack(pady=5)

        modify_fund_button = tk.Button(self.frame, text="Modify Fund", command=self.modify_fund)
        modify_fund_button.pack(pady=5)

        remove_fund_button = tk.Button(self.frame, text="Remove Fund", command=self.remove_fund)
        remove_fund_button.pack(pady=5)

        # Additional UI components like a list of funds, search functionality, etc.

    def add_fund(self):
        """Add a new fund to the database."""
        # Logic to add a fund (open a new window with a form, collect data, and save it)
        pass

    def modify_fund(self):
        """Modify an existing fund."""
        # Logic to modify a fund (select a fund, open a form with its data, allow modifications)
        pass

    def remove_fund(self):
        """Remove a fund from the database."""
        # Logic to remove a fund (select a fund, confirm deletion, and remove it)
        pass

    # Additional methods for CRUD operations can be added here
