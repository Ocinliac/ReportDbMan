# gui/modules/data_mgmt_components/share_class_management.py

import tkinter as tk
from tkinter import messagebox
from db.models import ShareClass
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy import create_engine

class ShareClassWindow:
    def __init__(self, parent, session, fund_id=None):
        self.session = session
        self.fund_id = fund_id
        self.window = tk.Toplevel(parent)
        self.window.title("Add Share Class")

        # Share Class Form
        self.fund_id_entry = self.create_form_entry("Fund ID", fund_id)
        self.short_name = self.create_form_entry("Short Name")
        self.status = self.create_form_entry("Status")
        self.share_class_type = self.create_form_entry("Share Class Type")
        self.distribution = self.create_form_entry("Distribution")

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_share_class)
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

    def save_share_class(self):
        """Saves the share class to the database."""
        share_class = ShareClass(
            fund_id=self.fund_id_entry.get(),
            short_name=self.short_name.get(),
            status=self.status.get(),
            share_class_type=self.share_class_type.get(),
            distribution=self.distribution.get()
        )
        self.session.add(share_class)
        self.session.commit()
        messagebox.showinfo("Success", "Share class added successfully!")
        self.window.destroy()  # Close the window after submission
