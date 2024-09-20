# File: /Users/nicolascailmail/PyProject/ReportDbMan/gui/modules/data_management_components/production_management/people_management.py

import tkinter as tk
from tkinter import ttk, Menu, messagebox
from db.models import People, TechnicalTable
from sqlalchemy.exc import SQLAlchemyError

from utils.Global_Function import populate_combobox


class PeopleManagement:
    def __init__(self, parent, session):
        self.session = session
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        label = tk.Label(self.frame, text="People Management", font=("Helvetica", 16))
        label.pack(pady=20)

        # Define columns for the Treeview
        columns = ("People ID", "Name", "Email", "Role")

        # Treeview for displaying people
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Define the column headers
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Add People button
        add_people_button = tk.Button(self.frame, text="Add People", command=self.open_add_people_window)
        add_people_button.pack(pady=5)

        # Bind right-click and double-click events
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_people()

    def load_people(self):
        """Loads people from the database into the Treeview."""
        # Clear the existing entries in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Query all people from the database and insert them into the Treeview
        for people in self.session.query(People).all():
            self.tree.insert(
                "", "end",
                values=(
                    people.people_id,
                    people.name,
                    people.email,
                    people.role
                )
            )

    def show_context_menu(self, event):
        """Shows a context menu on right-click."""
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            context_menu = Menu(self.frame, tearoff=0)
            context_menu.add_command(label="Modify People", command=self.modify_people)
            context_menu.add_command(label="Delete People", command=self.delete_people)
            context_menu.tk_popup(event.x_root, event.y_root)

    def on_double_click(self, event):
        """Handles double-click event to show people details."""
        selected_item = self.tree.selection()[0]
        people_id = self.tree.item(selected_item)['values'][0]
        self.show_people_details(people_id)

    def open_add_people_window(self):
        """Opens a window to add a new person."""
        PeopleWindow(self.frame, self.session, refresh_callback=self.load_people)

    def modify_people(self):
        """Opens a window to modify the selected person."""
        selected_item = self.tree.selection()[0]
        people_id = self.tree.item(selected_item)['values'][0]
        PeopleWindow(self.frame, self.session, people_id=people_id, refresh_callback=self.load_people)

    def delete_people(self):
        """Deletes the selected person from the database."""
        selected_item = self.tree.selection()[0]
        people_id = self.tree.item(selected_item)['values'][0]
        try:
            people = self.session.query(People).filter_by(people_id=people_id).one()
            self.session.delete(people)
            self.session.commit()
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Person deleted successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_people_details(self, people_id):
        """Shows detailed information about the selected person."""
        # Implement the logic to show detailed information about the person
        pass


class PeopleWindow:
    def __init__(self, parent, session, people_id=None, refresh_callback=None):
        self.session = session
        self.people_id = people_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Modify People" if people_id else "Add People")

        # People Form
        self.name_entry = self.create_form_entry("Name")
        self.email_entry = self.create_form_entry("Email")

        # Role Combobox (based on the 'role' category in the technical table)
        self.role_combobox = self.create_combobox("Role", TechnicalTable, "tt_value", "tt_id", filter_by={'tt_category': 'Roles'})

        # If modifying, load the existing people data
        if people_id:
            self.load_people_data()

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_people)
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

    def create_combobox(self, label_text, model, display_field, value_field, filter_by=None, on_select=None):
        """Creates a label and combobox populated with values from the technical table."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")

        combobox = ttk.Combobox(frame, state="readonly")
        populate_combobox(self.session, combobox, model, display_field, value_field, filter_by, on_select)
        combobox.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)

        return combobox

    def load_people_data(self):
        """Load existing people data into the form fields for modification."""
        people = self.session.query(People).filter_by(people_id=self.people_id).one()
        self.name_entry.insert(0, people.name)
        self.email_entry.insert(0, people.email)
        self.role_combobox.set(f"{people.role}")  # Set the role in the combobox

    def save_people(self):
        """Saves the people to the database."""
        try:
            if self.people_id:
                # Modify existing people
                people = self.session.query(People).filter_by(people_id=self.people_id).one()
                people.name = self.name_entry.get()
                people.email = self.email_entry.get()
                people.role = self.role_combobox.get().split(": ")[1]  # Get the role value from the combobox
            else:
                # Add new person
                people = People(
                    name=self.name_entry.get(),
                    email=self.email_entry.get(),
                    role=self.role_combobox.get().split(": ")[1]  # Get the role value from the combobox
                )
                self.session.add(people)

            self.session.commit()
            if self.refresh_callback:
                self.refresh_callback()
            messagebox.showinfo("Success", "Person saved successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()

