# gui/modules/data_mgmt_components/code_management.py

import tkinter as tk
from tkinter import messagebox
from db.models import FundCode
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy import create_engine

class FundCodesWindow:
    def __init__(self, parent, session, fund_id=None):
        self.session = session
        self.fund_id = fund_id
        self.window = tk.Toplevel(parent)
        self.window.title("Add Fund Codes")

        # Fund Codes Form
        self.fund_id_entry = self.create_form_entry("Fund ID", fund_id)
        self.code = self.create_form_entry("Code")
        self.portfolio_code = self.create_form_entry("Portfolio Code")
        self.portfolio_code_apo = self.create_form_entry("Portfolio Code APO")
        self.portfolio_code_tr = self.create_form_entry("Portfolio Code TR")
        self.cam_id = self.create_form_entry("CAM ID")
        self.lei = self.create_form_entry("LEI")

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_fund_code)
        submit_button.pack(pady=20)

    def create_form_entry(self, label_text, initial_value=None):
        """Creates a label and entry field for a form."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        if initial_value is not None:
            entry.insert(0, initial_value)
            entry.config(state='readonly')  # Make it readonly if provided
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)
        return entry

    def save_fund_code(self):
        """Saves the fund code to the database."""
        fund_code = FundCode(
            fund_id=self.fund_id_entry.get(),
            code=self.code.get(),
            portfolio_code=self.portfolio_code.get(),
            portfolio_code_apo=self.portfolio_code_apo.get(),
            portfolio_code_tr=self.portfolio_code_tr.get(),
            cam_id=self.cam_id.get(),
            lei=self.lei.get()
        )
        self.session.add(fund_code)
        self.session.commit()
        messagebox.showinfo("Success", "Fund code added successfully!")
        self.window.destroy()  # Close the window after submission
