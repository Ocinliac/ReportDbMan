import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from db.models import ProductionAssignment, People


class AssignmentWindow:
    def __init__(self, parent, session, production_id):
        self.session = session
        self.production_id = production_id
        self.window = tk.Toplevel(parent)
        self.window.title("Manage Assignment")

        # Create a notebook for the two roles
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True)

        # Create frames for Reporting Analyst and Portfolio Manager
        self.create_role_frame("Reporting Analyst")
        self.create_role_frame("Portfolio Manager")

    def create_role_frame(self, role):
        """Helper function to create and set up UI for a specific role frame."""
        frame = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(frame, text=role)

        # Search bar setup
        search_var = tk.StringVar()
        search_entry = self.create_search_bar(frame, role, search_var)

        # Listbox to display search results
        result_listbox = self.create_listbox(frame, height=5)

        # Button frame for Add/Remove functionality
        self.create_add_remove_buttons(frame, result_listbox, role)

        # Listbox to display selected people
        selected_listbox = self.create_listbox(frame, height=10)

        # Store listboxes and state in the frame
        frame.result_listbox = result_listbox
        frame.selected_listbox = selected_listbox
        frame.selected_people = []

        # Load existing assignments
        self.load_existing_assignments(role, frame)

        # Bind search bar update
        search_entry.bind("<KeyRelease>", lambda event: self.update_suggestions(role, frame, search_var))

    def create_search_bar(self, frame, role, search_var):
        """Helper function to create the search bar for a role."""
        search_label = tk.Label(frame, text=f"Search People ({role}):")
        search_label.pack(pady=5)
        search_entry = tk.Entry(frame, textvariable=search_var)
        search_entry.pack(pady=5)
        return search_entry

    def create_listbox(self, frame, height=5):
        """Helper function to create a Listbox widget."""
        listbox = tk.Listbox(frame, height=height)
        listbox.pack(pady=5)
        return listbox

    def create_add_remove_buttons(self, frame, result_listbox, role):
        """Helper function to create Add and Remove buttons."""
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=5)
        add_button = tk.Button(button_frame, text="Add >>",
                               command=lambda: self.add_person(result_listbox, role, frame))
        add_button.pack(side="left", padx=5)
        remove_button = tk.Button(button_frame, text="<< Remove",
                                  command=lambda: self.remove_person(frame, role))
        remove_button.pack(side="left", padx=5)

    def load_existing_assignments(self, role, frame):
        """Load existing assignments for a role into the selected_listbox."""
        try:
            assignments = self.session.query(ProductionAssignment).filter_by(
                production_id=self.production_id, AssignRole=role).order_by(ProductionAssignment.assignment_id).all()
            for assignment in assignments:
                person = self.session.query(People).filter_by(people_id=assignment.people_id).one()
                person_display = f"{person.people_id}: {person.name}"
                frame.selected_people.append(person_display)
                frame.selected_listbox.insert(tk.END, person_display)
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"An error occurred while loading assignments: {e}")

    def update_suggestions(self, role, frame, search_var):
        """Update the suggestions in the result_listbox based on the search term."""
        search_term = search_var.get().strip()
        frame.result_listbox.delete(0, tk.END)

        try:
            people_query = self.session.query(People).filter(func.lower(People.role) == func.lower(role))

            # Apply search filter if a search term is provided
            if search_term:
                people_query = people_query.filter(func.lower(People.name).ilike(f"%{search_term.lower()}%"))

            people = people_query.all()

            for person in people:
                person_display = f"{person.people_id}: {person.name}"
                if person_display not in frame.selected_people:
                    frame.result_listbox.insert(tk.END, person_display)

        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"An error occurred while searching for people: {e}")

    def add_person(self, result_listbox, role, frame):
        """Add the selected person to the selected_listbox and update the production assignment."""
        selected = result_listbox.get(tk.ACTIVE)
        if selected and selected not in frame.selected_people:
            frame.selected_people.append(selected)
            frame.selected_listbox.insert(tk.END, selected)
            self.update_production_assignment(role, frame)

    def remove_person(self, frame, role):
        """Remove the selected person from the selected_listbox and update the production assignment."""
        selected = frame.selected_listbox.get(tk.ACTIVE)
        if selected in frame.selected_people:
            frame.selected_people.remove(selected)
            frame.selected_listbox.delete(tk.ACTIVE)
            self.update_production_assignment(role, frame)

    def update_production_assignment(self, role, frame):
        """Update the production assignment in the database."""
        try:
            # Remove the current assignments for the given role
            self.session.query(ProductionAssignment).filter_by(production_id=self.production_id,
                                                               AssignRole=role).delete()
            self.session.commit()

            # Re-insert selected people with the updated order
            for idx, person in enumerate(frame.selected_people, start=1):
                people_id = int(person.split(":")[0])
                new_assignment = ProductionAssignment(
                    production_id=self.production_id,
                    people_id=people_id,
                    AssignRole=role,
                    order=idx
                )
                self.session.add(new_assignment)

            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred while updating assignments: {e}")
