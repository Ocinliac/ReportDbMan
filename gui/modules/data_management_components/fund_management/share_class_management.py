# gui/modules/data_mgmt_components/share_class_management.py

import tkinter as tk
from tkinter import messagebox

from sqlalchemy.exc import SQLAlchemyError

from db.models import ShareClass
from sqlalchemy.orm import sessionmaker
from config.settings import DATABASE_URL
from sqlalchemy import create_engine


class ShareClassWindow:
    def __init__(self, parent, session, fund_id=None, share_class_id=None, refresh_callback=None):
        self.session = session
        self.fund_id = fund_id
        self.share_class_id = share_class_id
        self.refresh_callback = refresh_callback  # Store the callback function to refresh the Treeview
        self.window = tk.Toplevel(parent)
        self.window.title("Modify Share Class" if share_class_id else "Add Share Class")

        # Share Class Form
        self.fund_id_entry = self.create_form_entry("Fund ID", fund_id)
        self.short_name = self.create_form_entry("Short Name")
        self.status = self.create_form_entry("Status")
        self.share_class_type = self.create_form_entry("Share Class Type")
        self.distribution = self.create_form_entry("Distribution")

        # If modifying, load the existing share class data
        if share_class_id:
            self.load_share_class_data()

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

    def load_share_class_data(self):
        """Load existing share class data into the form fields for modification."""
        share_class = self.session.query(ShareClass).filter_by(share_class_id=self.share_class_id).one()
        self.short_name.insert(0, share_class.short_name)
        self.status.insert(0, share_class.status)
        self.share_class_type.insert(0, share_class.share_class_type)
        self.distribution.insert(0, share_class.distribution)

    def save_share_class(self):
        """Saves the share class to the database."""
        try:
            if self.share_class_id:
                # Modify existing share class
                share_class = self.session.query(ShareClass).filter_by(share_class_id=self.share_class_id).one()
                share_class.short_name = self.short_name.get()
                share_class.status = self.status.get()
                share_class.share_class_type = self.share_class_type.get()
                share_class.distribution = self.distribution.get()
            else:
                # Add new share class
                share_class = ShareClass(
                    fund_id=self.fund_id_entry.get(),
                    short_name=self.short_name.get(),
                    status=self.status.get(),
                    share_class_type=self.share_class_type.get(),
                    distribution=self.distribution.get()
                )
                self.session.add(share_class)

            self.session.commit()  # Commit the transaction
            messagebox.showinfo("Success", "Share class saved successfully!")

            if self.refresh_callback:
                self.refresh_callback()  # Call the refresh function to update the Treeview
        except SQLAlchemyError as e:
            self.session.rollback()  # Rollback the transaction on error
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()  # Close the window after submission

