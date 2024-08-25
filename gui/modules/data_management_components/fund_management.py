# gui/modules/data_management_components/fund_management.py

import tkinter as tk
# gui/modules/data_management_components/fund_management.py

import tkinter as tk
from tkinter import ttk
from sqlalchemy.orm import sessionmaker
from db.models import Fund
from config.settings import DATABASE_URL
from sqlalchemy import create_engine

class FundManagement:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        self.engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for fund management."""
        title = tk.Label(self.frame, text="Fund Management", font=("Helvetica", 16))
        title.pack(pady=10)

        # Define columns for the Treeview
        columns = ("Fund ID", "Official Name", "Marketing Name", "Asset Class", "Legal Structure", "Creation Date",
                   "Closure Date", "Status", "ESG", "SFDR Article", "Portfolio Manager", "Currency", "Valuation",
                   "Management Company", "Distribution Company", "Benchmark Indicator")

        # Treeview for displaying funds
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Define the column headers
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Add Fund button
        add_fund_button = tk.Button(self.frame, text="Add Fund", command=self.open_add_fund_window)
        add_fund_button.pack(pady=5)

        self.load_funds()

    def load_funds(self):
        """Loads funds from the database into the Treeview."""
        # Clear the existing entries in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Query all funds from the database and insert them into the Treeview
        for fund in self.session.query(Fund).all():
            self.tree.insert(
                "", "end",
                values=(
                    fund.fund_id,
                    fund.official_name,
                    fund.marketing_name,
                    fund.asset_class,
                    fund.legal_structure,
                    fund.creation_date,
                    fund.closure_date,
                    fund.status,
                    fund.esg,
                    fund.sfdr_article,
                    fund.portfolio_manager,
                    fund.currency,
                    fund.valuation,
                    fund.management_company,
                    fund.distribution_company,
                    fund.benchmark_indicator
                )
            )

    def open_add_fund_window(self):
        """Opens the window to add a new fund."""
        FundWindow(self.parent, self.session, self.tree)


    def show_context_menu(self, event):
        """Displays a context menu to add a share class to the selected fund."""
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            fund_id = self.tree.item(selected_item)['values'][0]
            context_menu = Menu(self.parent, tearoff=0)
            context_menu.add_command(label="Add Share Class", command=lambda: self.open_add_share_class_window(fund_id))
            context_menu.tk_popup(event.x_root, event.y_root)

    def open_add_share_class_window(self, fund_id):
        """Opens the window to add a share class for the selected fund."""
        ShareClassWindow(self.parent, self.session, fund_id)


import tkinter as tk
from datetime import datetime
from gui.modules.data_management_components.common_widget import create_form_entry, create_button
from db.models import Fund
from sqlalchemy.exc import SQLAlchemyError
from tkinter import messagebox

class FundWindow:
    def __init__(self, parent, session, tree):
        self.session = session
        self.tree = tree
        self.window = tk.Toplevel(parent)
        self.window.title("Add Fund")

        # Fund Form
        self.official_name = create_form_entry(self.window, "Official Name")
        self.marketing_name = create_form_entry(self.window, "Marketing Name")
        self.asset_class = create_form_entry(self.window, "Asset Class")
        self.legal_structure = create_form_entry(self.window, "Legal Structure")
        self.creation_date = create_form_entry(self.window, "Creation Date (YYYY-MM-DD)")
        self.closure_date = create_form_entry(self.window, "Closure Date (optional, YYYY-MM-DD)")
        self.status = create_form_entry(self.window, "Status")
        self.esg = create_form_entry(self.window, "ESG (True/False)")
        self.sfdr_article = create_form_entry(self.window, "SFDR Article")
        self.portfolio_manager = create_form_entry(self.window, "Portfolio Manager")
        self.currency = create_form_entry(self.window, "Currency")
        self.valuation = create_form_entry(self.window, "Valuation")
        self.management_company = create_form_entry(self.window, "Management Company")
        self.distribution_company = create_form_entry(self.window, "Distribution Company")
        self.benchmark_indicator = create_form_entry(self.window, "Benchmark Indicator")

        # Buttons to add Fund Codes and Share Classes
        create_button(self.window, "Submit", self.save_fund)

    def save_fund(self):
        """Saves the fund to the database."""
        try:
            # Convert the creation_date and closure_date to date objects
            creation_date = datetime.strptime(self.creation_date.get(), '%Y-%m-%d').date()
            closure_date_str = self.closure_date.get()
            closure_date = datetime.strptime(closure_date_str, '%Y-%m-%d').date() if closure_date_str else None

            fund = Fund(
                official_name=self.official_name.get(),
                marketing_name=self.marketing_name.get(),
                asset_class=self.asset_class.get(),
                legal_structure=self.legal_structure.get(),
                creation_date=creation_date,  # Use the converted date object
                closure_date=closure_date,  # Use the converted date object or None
                status=self.status.get(),
                esg=self.esg.get().lower() == 'true',
                sfdr_article=self.sfdr_article.get(),
                portfolio_manager=self.portfolio_manager.get(),
                currency=self.currency.get(),
                valuation=self.valuation.get(),
                management_company=self.management_company.get(),
                distribution_company=self.distribution_company.get(),
                benchmark_indicator=self.benchmark_indicator.get()
            )
            self.session.add(fund)
            self.session.commit()  # Commit the transaction
            self.tree.insert("", "end", values=(fund.fund_id, fund.official_name, fund.status))
            messagebox.showinfo("Success", "Fund added successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()  # Rollback the transaction on error
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()  # Close the window after submission

