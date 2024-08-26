# gui/modules/data_management_components/fund_management.py

import tkinter as tk
from tkinter import ttk, Menu, messagebox
from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import Fund, ShareClass, FundCode
from config.settings import DATABASE_URL
from sqlalchemy import create_engine
from gui.modules.data_management_components.share_class_management import ShareClassWindow
from gui.modules.data_management_components.code_management import FundCodesWindow
from gui.modules.data_management_components.common_widget import create_form_entry, create_button


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
        columns = (
            "Fund ID", "Official Name", "Marketing Name", "Asset Class", "Legal Structure", "Creation Date",
            "Closure Date", "Status", "ESG", "SFDR Article", "Portfolio Manager", "Currency", "Valuation",
            "Management Company", "Distribution Company", "Benchmark Indicator"
        )

        # Treeview for displaying funds
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Define the column headers
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Add Fund button
        add_fund_button = tk.Button(self.frame, text="Add Fund", command=self.open_add_fund_window)
        add_fund_button.pack(pady=5)

        # Bind right-click and double-click events
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

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

    def show_context_menu(self, event):
        """Shows a context menu on right-click."""
        # Identify the item under the cursor
        selected_item = self.tree.identify_row(event.y)
        print(f"Right-click detected. Selected item: {selected_item}")  # Debugging statement

        if selected_item:
            # Set the selection to the item under the cursor
            self.tree.selection_set(selected_item)
            print("Item selected for context menu.")  # Debugging statement

            context_menu = Menu(self.parent, tearoff=0)
            context_menu.add_command(label="Add Share Class", command=self.add_share_class)
            context_menu.add_command(label="Add Codes", command=self.add_codes)
            context_menu.add_command(label="Modify Fund", command=self.modify_fund)
            context_menu.add_command(label="Delete Fund", command=self.delete_fund)

            context_menu.tk_popup(event.x_root, event.y_root)
            print("Context menu should be visible.")  # Debugging statement
        else:
            # Clear the selection if right-clicked on empty space
            self.tree.selection_remove(self.tree.selection())
            print("Right-click was on an empty space. No context menu shown.")  # Debugging statement

    def on_double_click(self, event):
        """Handles double-click event to show share classes linked to the fund."""
        selected_item = self.tree.selection()[0]
        fund_id = self.tree.item(selected_item)['values'][0]
        self.show_share_classes_and_codes(fund_id)

    def open_add_fund_window(self):
        """Opens a window to add a new fund."""
        FundWindow(self.parent, self.session, self.tree)

    def add_share_class(self):
        """Opens a window to add a share class to the selected fund."""
        selected_item = self.tree.selection()[0]
        fund_id = self.tree.item(selected_item)['values'][0]
        ShareClassWindow(self.parent, self.session, fund_id)

    def add_codes(self):
        """Opens a window to add codes to the selected fund."""
        selected_item = self.tree.selection()[0]
        fund_id = self.tree.item(selected_item)['values'][0]
        FundCodesWindow(self.parent, self.session, fund_id)

    def modify_fund(self):
        """Opens a window to modify the selected fund."""
        selected_item = self.tree.selection()[0]
        fund_id = self.tree.item(selected_item)['values'][0]
        FundWindow(self.parent, self.session, self.tree, fund_id=fund_id)

    def delete_fund(self):
        """Deletes the selected fund from the database."""
        selected_item = self.tree.selection()[0]
        fund_id = self.tree.item(selected_item)['values'][0]
        try:
            fund = self.session.query(Fund).filter_by(fund_id=fund_id).one()
            self.session.delete(fund)
            self.session.commit()
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Fund deleted successfully!")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def refresh_share_class_tree(self, tree, fund_id):
        """Refresh the share classes in the Treeview."""
        # Clear the existing entries in the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Query all share classes for the given fund and insert them into the Treeview
        share_classes = self.session.query(ShareClass).filter_by(fund_id=fund_id).all()
        for sc in share_classes:
            tree.insert("", "end",
                        values=(sc.share_class_id, sc.short_name, sc.status, sc.share_class_type, sc.distribution))

    def refresh_fund_code_tree(self, tree, fund_id):
        """Refreshes the fund code tree with updated data."""
        # Clear existing entries
        for row in tree.get_children():
            tree.delete(row)

        # Query and insert updated data
        fund_codes = self.session.query(FundCode).filter_by(fund_id=fund_id).all()
        for fc in fund_codes:
            tree.insert("", "end", values=(
                fc.fund_code_id, fc.code, fc.portfolio_code, fc.portfolio_code_apo, fc.portfolio_code_tr, fc.cam_id,
                fc.lei))

    def show_share_classes_and_codes(self, fund_id):
        """Opens a new window with tabs to show share classes and codes linked to the selected fund."""
        window = tk.Toplevel(self.parent)
        window.title("Share Classes and Fund Codes")

        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True)

        # Share Classes Tab
        share_classes_frame = tk.Frame(notebook)
        notebook.add(share_classes_frame, text="Share Classes")

        share_classes_tree = ttk.Treeview(share_classes_frame,
                                          columns=("Share Class ID", "Short Name", "Status", "Type", "Distribution"),
                                          show="headings")
        share_classes_tree.pack(fill="both", expand=True)

        for col in ("Share Class ID", "Short Name", "Status", "Type", "Distribution"):
            share_classes_tree.heading(col, text=col)

        self.refresh_share_class_tree(share_classes_tree, fund_id)

        # Bind right-click event to open Share Class context menu
        share_classes_tree.bind("<Button-2>",
                                lambda event: self.show_share_class_context_menu(event, share_classes_tree))

        # Fund Codes Tab
        fund_codes_frame = tk.Frame(notebook)
        notebook.add(fund_codes_frame, text="Fund Codes")

        fund_codes_tree = ttk.Treeview(fund_codes_frame, columns=(
            "Fund Code ID", "Code", "Portfolio Code", "Portfolio Code APO", "Portfolio Code TR", "CAM ID", "LEI"),
                                       show="headings")
        fund_codes_tree.pack(fill="both", expand=True)

        # Hide the Fund Code ID column
        fund_codes_tree.heading("Fund Code ID", text="", anchor='w')
        fund_codes_tree.column("Fund Code ID", width=0, stretch=tk.NO)  # Hidden column

        for col in ("Code", "Portfolio Code", "Portfolio Code APO", "Portfolio Code TR", "CAM ID", "LEI"):
            fund_codes_tree.heading(col, text=col)

        fund_codes = self.session.query(FundCode).filter_by(fund_id=fund_id).all()
        for fc in fund_codes:
            fund_codes_tree.insert("", "end", values=(
                fc.fund_code_id, fc.code, fc.portfolio_code, fc.portfolio_code_apo, fc.portfolio_code_tr, fc.cam_id,
                fc.lei))

        # Bind right-click event to open Fund Codes context menu
        fund_codes_tree.bind("<Button-2>", lambda event: self.show_fund_code_context_menu(event, fund_codes_tree))

        # Display message if no fund codes exist
        if not fund_codes_tree.get_children():
            fund_codes_tree.bind("<Button-1>",
                                 lambda event: self.show_empty_message("No fund codes linked to this fund."))

    def modify_share_class(self, tree):
        """Opens a window to modify the selected share class."""
        selected_item = tree.selection()[0]
        share_class_id = tree.item(selected_item)['values'][0]
        share_class = self.session.query(ShareClass).filter_by(share_class_id=share_class_id).one()
        ShareClassWindow(self.parent, self.session, share_class.fund_id, share_class_id=share_class_id,
                         refresh_callback=lambda: self.refresh_share_class_tree(tree, share_class.fund_id))

    def show_share_class_context_menu(self, event, tree):
        """Shows a context menu for the share classes."""
        selected_item = tree.identify_row(event.y)
        if selected_item:
            tree.selection_set(selected_item)
            context_menu = Menu(self.parent, tearoff=0)
            context_menu.add_command(label="Modify Share Class", command=lambda: self.modify_share_class(tree))
            context_menu.add_command(label="Delete Share Class", command=lambda: self.delete_share_class(tree))
            context_menu.tk_popup(event.x_root, event.y_root)

    def show_fund_code_context_menu(self, event, tree):
        """Shows a context menu for the fund codes."""
        selected_item = tree.identify_row(event.y)
        if selected_item:
            tree.selection_set(selected_item)
            context_menu = Menu(self.parent, tearoff=0)
            context_menu.add_command(label="Modify Fund Code", command=lambda: self.modify_fund_code(tree))
            context_menu.add_command(label="Delete Fund Code", command=lambda: self.delete_fund_code(tree))
            context_menu.tk_popup(event.x_root, event.y_root)

    def modify_fund_code(self, tree):
        """Opens a window to modify the selected fund code."""
        try:
            selected_item = tree.selection()[0]
            fund_code_id = tree.item(selected_item)['values'][0]  # Get the hidden fund_code_id
            fund_code = self.session.query(FundCode).filter_by(fund_code_id=fund_code_id).one()

            # Pass the refresh callback when opening the FundCodesWindow
            FundCodesWindow(
                self.parent,
                self.session,
                fund_code.fund_id,
                fund_code_id=fund_code_id,
                refresh_callback=lambda: self.refresh_fund_code_tree(tree, fund_code.fund_id)
            )

        except IndexError:
            messagebox.showerror("Selection Error", "No fund code selected.")
        except sqlalchemy.exc.NoResultFound:
            messagebox.showerror("Not Found", "The selected fund code was not found in the database.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def delete_fund_code(self, tree):
        """Deletes the selected fund code from the database."""
        selected_item = tree.selection()[0]
        fund_code_id = tree.item(selected_item)['values'][0]
        try:
            fund_code = self.session.query(FundCode).filter_by(fund_code_id=fund_code_id).one()
            self.session.delete(fund_code)
            self.session.commit()
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Fund code deleted successfully!")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def delete_share_class(self, tree):
        """Deletes the selected share class from the database."""
        selected_item = tree.selection()[0]
        share_class_id = tree.item(selected_item)['values'][0]
        try:
            share_class = self.session.query(ShareClass).filter_by(share_class_id=share_class_id).one()
            self.session.delete(share_class)
            self.session.commit()
            tree.delete(selected_item)
            messagebox.showinfo("Success", "Share class deleted successfully!")
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")


class FundWindow:
    def __init__(self, parent, session, tree, fund_id=None):
        self.session = session
        self.tree = tree
        self.fund_id = fund_id  # Store the fund ID to know if we are modifying an existing fund
        self.window = tk.Toplevel(parent)
        self.window.title("Add Fund" if not fund_id else "Modify Fund")

        # Fund Form Entries
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

        # If fund_id is provided, load the existing fund data
        if fund_id:
            self.load_fund_data()

        # Submit Button
        create_button(self.window, "Submit", self.save_fund)

    def load_fund_data(self):
        """Load existing fund data into the form fields for modification."""
        fund = self.session.query(Fund).filter_by(fund_id=self.fund_id).one()

        # Populate the form entries with the existing fund data
        self.official_name.insert(0, fund.official_name)
        self.marketing_name.insert(0, fund.marketing_name)
        self.asset_class.insert(0, fund.asset_class)
        self.legal_structure.insert(0, fund.legal_structure)
        self.creation_date.insert(0, fund.creation_date.strftime('%Y-%m-%d'))
        if fund.closure_date:
            self.closure_date.insert(0, fund.closure_date.strftime('%Y-%m-%d'))
        self.status.insert(0, fund.status)
        self.esg.insert(0, str(fund.esg))
        self.sfdr_article.insert(0, fund.sfdr_article)
        self.portfolio_manager.insert(0, fund.portfolio_manager)
        self.currency.insert(0, fund.currency)
        self.valuation.insert(0, fund.valuation)
        self.management_company.insert(0, fund.management_company)
        self.distribution_company.insert(0, fund.distribution_company)
        self.benchmark_indicator.insert(0, fund.benchmark_indicator)

    def save_fund(self):
        """Saves the fund to the database."""
        try:
            # Convert the creation_date and closure_date to date objects
            creation_date = datetime.strptime(self.creation_date.get(), '%Y-%m-%d').date()
            closure_date_str = self.closure_date.get()
            closure_date = datetime.strptime(closure_date_str, '%Y-%m-%d').date() if closure_date_str else None

            if self.fund_id:
                # Modify existing fund
                fund = self.session.query(Fund).filter_by(fund_id=self.fund_id).one()
                fund.official_name = self.official_name.get()
                fund.marketing_name = self.marketing_name.get()
                fund.asset_class = self.asset_class.get()
                fund.legal_structure = self.legal_structure.get()
                fund.creation_date = creation_date
                fund.closure_date = closure_date
                fund.status = self.status.get()
                fund.esg = self.esg.get().lower() == 'true'
                fund.sfdr_article = self.sfdr_article.get()
                fund.portfolio_manager = self.portfolio_manager.get()
                fund.currency = self.currency.get()
                fund.valuation = self.valuation.get()
                fund.management_company = self.management_company.get()
                fund.distribution_company = self.distribution_company.get()
                fund.benchmark_indicator = self.benchmark_indicator.get()
            else:
                # Add new fund
                fund = Fund(
                    official_name=self.official_name.get(),
                    marketing_name=self.marketing_name.get(),
                    asset_class=self.asset_class.get(),
                    legal_structure=self.legal_structure.get(),
                    creation_date=creation_date,
                    closure_date=closure_date,
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

            self.session.commit()
            # Refresh the entire Treeview with all funds
            self.refresh_treeview()
            messagebox.showinfo("Success", "Fund saved successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()

    def refresh_treeview(self):
        """Refresh the Treeview with all funds after adding/modifying a fund."""
        # Clear the existing entries in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Query all funds and reinsert them into the Treeview
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


