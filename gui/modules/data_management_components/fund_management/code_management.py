# gui/modules/data_mgmt_components/code_management.py

import tkinter as tk
from tkinter import messagebox

from sqlalchemy.exc import SQLAlchemyError

from db.models import FundCode
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy import create_engine


class FundCodesWindow:
    def __init__(self, parent, session, fund_id=None, fund_code_id=None, refresh_callback=None):
        self.session = session
        self.fund_id = fund_id
        self.fund_code_id = fund_code_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.parent = parent  # Store parent to call refresh methods
        self.window.title("Modify Fund Code" if fund_code_id else "Add Fund Code")

        # Fund Codes Form
        self.code_entry = self.create_form_entry("Code")
        self.portfolio_code_entry = self.create_form_entry("Portfolio Code")
        self.portfolio_code_apo_entry = self.create_form_entry("Portfolio Code APO")
        self.portfolio_code_tr_entry = self.create_form_entry("Portfolio Code TR")
        self.cam_id_entry = self.create_form_entry("CAM ID")
        self.lei_entry = self.create_form_entry("LEI")

        # If modifying, load the existing fund code data
        if fund_code_id:
            self.load_fund_code_data()

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_fund_code)
        submit_button.pack(pady=20)

    def create_form_entry(self, label_text, initial_value=None):
        """Creates a label and entry field for a form."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        if initial_value:
            entry.insert(0, initial_value)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)
        return entry

    def load_fund_code_data(self):
        """Load existing fund code data into the form fields for modification."""
        fund_code = self.session.query(FundCode).filter_by(fund_code_id=self.fund_code_id).one()
        self.code_entry.insert(0, fund_code.code)
        self.portfolio_code_entry.insert(0, fund_code.portfolio_code)
        self.portfolio_code_apo_entry.insert(0, fund_code.portfolio_code_apo)
        self.portfolio_code_tr_entry.insert(0, fund_code.portfolio_code_tr)
        self.cam_id_entry.insert(0, fund_code.cam_id)
        self.lei_entry.insert(0, fund_code.lei)

    def save_fund_code(self):
        """Saves the fund code to the database."""
        try:
            if self.fund_code_id:
                # Modify existing fund code
                fund_code = self.session.query(FundCode).filter_by(fund_code_id=self.fund_code_id).one()
                fund_code.code = self.code_entry.get()
                fund_code.portfolio_code = self.portfolio_code_entry.get()
                fund_code.portfolio_code_apo = self.portfolio_code_apo_entry.get()
                fund_code.portfolio_code_tr = self.portfolio_code_tr_entry.get()
                fund_code.cam_id = self.cam_id_entry.get()
                fund_code.lei = self.lei_entry.get()
            else:
                # Add new fund code
                fund_code = FundCode(
                    fund_id=self.fund_id,
                    code=self.code_entry.get(),
                    portfolio_code=self.portfolio_code_entry.get(),
                    portfolio_code_apo=self.portfolio_code_apo_entry.get(),
                    portfolio_code_tr=self.portfolio_code_tr_entry.get(),
                    cam_id=self.cam_id_entry.get(),
                    lei=self.lei_entry.get()
                )
                self.session.add(fund_code)

            self.session.commit()  # Commit the transaction
            messagebox.showinfo("Success", "Fund code saved successfully!")

            # Call the refresh callback to update the Treeview
            if self.refresh_callback:
                self.refresh_callback()

        except SQLAlchemyError as e:
            self.session.rollback()  # Rollback the transaction on error
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()  # Close the window after submission
# gui/modules/data_management_components/code_management.py

import tkinter as tk
from tkinter import messagebox

from sqlalchemy.exc import SQLAlchemyError
from db.models import ShareClassCode


class ShareClassCodeWindow:
    def __init__(self, parent, session, share_class_id=None, share_class_code_id=None, refresh_callback=None):
        self.session = session
        self.share_class_id = share_class_id
        self.share_class_code_id = share_class_code_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.parent = parent
        self.window.title("Modify Share Class Code" if share_class_code_id else "Add Share Class Code")

        # Share Class Code Form
        self.code_entry = self.create_form_entry("Code")
        self.isin_entry = self.create_form_entry("ISIN")
        self.series_code_entry = self.create_form_entry("Series Code")
        self.gfc_fund_entry = self.create_form_entry("GFC Fund")

        # If modifying, load the existing share class code data
        if share_class_code_id:
            self.load_share_class_code_data()

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_share_class_code)
        submit_button.pack(pady=20)

    def create_form_entry(self, label_text, initial_value=None):
        """Creates a label and entry field for a form."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        if initial_value:
            entry.insert(0, initial_value)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)
        return entry

    def load_share_class_code_data(self):
        """Load existing share class code data into the form fields for modification."""
        share_class_code = self.session.query(ShareClassCode).filter_by(share_class_code_id=self.share_class_code_id).one()
        self.code_entry.insert(0, share_class_code.code)
        self.isin_entry.insert(0, share_class_code.isin)
        self.series_code_entry.insert(0, share_class_code.series_code)
        self.gfc_fund_entry.insert(0, share_class_code.gfc_fund)

    def save_share_class_code(self):
        """Saves the share class code to the database."""
        try:
            if self.share_class_code_id:
                # Modify existing share class code
                share_class_code = self.session.query(ShareClassCode).filter_by(
                    share_class_code_id=self.share_class_code_id).one()
                # update fields
                share_class_code.code = self.code_entry.get()
                share_class_code.isin = self.isin_entry.get()
                share_class_code.series_code = self.series_code_entry.get()
                share_class_code.gfc_fund = self.gfc_fund_entry.get()
            else:
                # Add new share class code
                share_class_code = ShareClassCode(
                    share_class_id=self.share_class_id,
                    code=self.code_entry.get(),
                    isin=self.isin_entry.get(),
                    series_code=self.series_code_entry.get(),
                    gfc_fund=self.gfc_fund_entry.get()
                )
                self.session.add(share_class_code)

            self.session.commit()
            if self.refresh_callback:
                self.refresh_callback()  # Refresh the TreeView after saving
            messagebox.showinfo("Success", "Share class code saved successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()  # Close the window after submission





