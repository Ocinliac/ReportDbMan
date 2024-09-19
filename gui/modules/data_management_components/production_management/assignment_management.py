# File: /Users/nicolascailmail/PyProject/ReportDbMan/gui/modules/data_management_components/production_management/assignment_management.py

import tkinter as tk
from tkinter import ttk, Menu, messagebox
from db.models import ProductionAssignment
from sqlalchemy.exc import SQLAlchemyError

class AssignmentManagement:
    def __init__(self, parent, session):
        self.session = session
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        label = tk.Label(self.frame, text="Assignment Management", font=("Helvetica", 16))
        label.pack(pady=20)

        # Define columns for the Treeview
        columns = ("Assignment ID", "Production ID", "People ID", "Role")

        # Treeview for displaying assignments
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")

        # Define the column headers
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Add Assignment button
        add_assignment_button = tk.Button(self.frame, text="Add Assignment", command=self.open_add_assignment_window)
        add_assignment_button.pack(pady=5)

        # Bind right-click and double-click events
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_assignments()

    def load_assignments(self):
        """Loads assignments from the database into the Treeview."""
        # Clear the existing entries in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Query all assignments from the database and insert them into the Treeview
        for assignment in self.session.query(ProductionAssignment).all():
            self.tree.insert(
                "", "end",
                values=(
                    assignment.assignment_id,
                    assignment.production_id,
                    assignment.people_id,
                    assignment.role
                )
            )

    def show_context_menu(self, event):
        """Shows a context menu on right-click."""
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            context_menu = Menu(self.frame, tearoff=0)
            context_menu.add_command(label="Modify Assignment", command=self.modify_assignment)
            context_menu.add_command(label="Delete Assignment", command=self.delete_assignment)
            context_menu.tk_popup(event.x_root, event.y_root)

    def on_double_click(self, event):
        """Handles double-click event to show assignment details."""
        selected_item = self.tree.selection()[0]
        assignment_id = self.tree.item(selected_item)['values'][0]
        self.show_assignment_details(assignment_id)

    def open_add_assignment_window(self):
        """Opens a window to add a new assignment."""
        AssignmentWindow(self.frame, self.session, refresh_callback=self.load_assignments)

    def modify_assignment(self):
        """Opens a window to modify the selected assignment."""
        selected_item = self.tree.selection()[0]
        assignment_id = self.tree.item(selected_item)['values'][0]
        AssignmentWindow(self.frame, self.session, assignment_id=assignment_id, refresh_callback=self.load_assignments)

    def delete_assignment(self):
        """Deletes the selected assignment from the database."""
        selected_item = self.tree.selection()[0]
        assignment_id = self.tree.item(selected_item)['values'][0]
        try:
            assignment = self.session.query(ProductionAssignment).filter_by(assignment_id=assignment_id).one()
            self.session.delete(assignment)
            self.session.commit()
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Assignment deleted successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_assignment_details(self, assignment_id):
        """Shows detailed information about the selected assignment."""
        # Implement the logic to show detailed information about the assignment
        pass


class AssignmentWindow:
    def __init__(self, parent, session, assignment_id=None, refresh_callback=None):
        self.session = session
        self.assignment_id = assignment_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Modify Assignment" if assignment_id else "Add Assignment")

        # Assignment Form
        self.production_id_entry = self.create_form_entry("Production ID")
        self.people_id_entry = self.create_form_entry("People ID")
        self.role_entry = self.create_form_entry("Role")

        # If modifying, load the existing assignment data
        if assignment_id:
            self.load_assignment_data()

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_assignment)
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

    def load_assignment_data(self):
        """Load existing assignment data into the form fields for modification."""
        assignment = self.session.query(ProductionAssignment).filter_by(assignment_id=self.assignment_id).one()
        self.production_id_entry.insert(0, assignment.production_id)
        self.people_id_entry.insert(0, assignment.people_id)
        self.role_entry.insert(0, assignment.role)

    def save_assignment(self):
        """Saves the assignment to the database."""
        try:
            if self.assignment_id:
                # Modify existing assignment
                assignment = self.session.query(ProductionAssignment).filter_by(assignment_id=self.assignment_id).one()
                assignment.production_id = self.production_id_entry.get()
                assignment.people_id = self.people_id_entry.get()
                assignment.role = self.role_entry.get()
            else:
                # Add new assignment
                assignment = ProductionAssignment(
                    production_id=self.production_id_entry.get(),
                    people_id=self.people_id_entry.get(),
                    role=self.role_entry.get()
                )
                self.session.add(assignment)

            self.session.commit()
            if self.refresh_callback:
                self.refresh_callback()
            messagebox.showinfo("Success", "Assignment saved successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.window.destroy()
