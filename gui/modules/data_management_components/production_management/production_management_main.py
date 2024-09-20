import tkinter as tk
from tkinter import ttk, Menu, messagebox
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import Production
from config.settings import DATABASE_URL
from gui.modules.data_management_components.production_management.assignment_management import AssignmentWindow
from gui.modules.data_management_components.production_management.people_management import PeopleManagement


class ProductionManagement:
    def __init__(self, parent, session):
        self.session = session
        # Create the main frame for the Production Management tab
        self.parent = parent
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        # Create a notebook for sub-tabs inside Production Management
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        # Create sub-tabs for Production, People, and Assignment management
        production_sub_tab = tk.Frame(self.notebook)
        people_sub_tab = tk.Frame(self.notebook)


        # Add sub-tabs to the notebook
        self.notebook.add(production_sub_tab, text="Production")
        self.notebook.add(people_sub_tab, text="People")


        # Initialize sub-tab content
        self.setup_production_ui(production_sub_tab)
        self.setup_people_management_ui(people_sub_tab)

    def setup_production_ui(self, tab):
        """Set up the user interface for production management."""
        # Title Label for the Production Management tab
        title = tk.Label(tab, text="Production Management", font=("Helvetica", 16))
        title.pack(pady=10)

        # Define columns for the Treeview based on the new table structure
        columns = (
            "Production ID", "Fund ID", "Share Class ID", "Potential Data Source", "Comment",
            "Output File Name", "Due Days", "Production Type", "Data Point", "Language",
            "Country Distribution", "Recipient", "Distribution Mode", "Data Source Used", "PM Validation"
        )

        # Treeview for displaying production records
        self.tree = ttk.Treeview(tab, columns=columns, show="headings")

        # Define the column headers
        for col in columns:
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        # Add Production button
        add_production_button = tk.Button(tab, text="Add Production", command=self.open_add_production_window)
        add_production_button.pack(pady=5)

        # Bind right-click and double-click events
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_productions()

    def setup_people_management_ui(self, tab):
        """Setup the UI for People Management sub-tab."""
        PeopleManagement(tab, self.session)  # Initialize PeopleManagement
    def load_productions(self):
        """Loads productions from the database into the Treeview."""
        # Clear the existing entries in the Treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Query all production records from the database
        for production in self.session.query(Production).all():
            self.tree.insert(
                "", "end",
                values=(
                    production.production_id,
                    production.fund_id,
                    production.share_class_id,
                    production.potential_data_source,
                    production.comment,
                    production.output_file_name,
                    production.due_days,
                    production.production_type,
                    production.data_point,
                    production.language,
                    production.country_distribution,
                    production.recipient,
                    production.distribution_mode,
                    production.data_source_used,
                    production.pm_validation
                )
            )

    def show_context_menu(self, event):
        """Shows a context menu on right-click."""
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            context_menu = Menu(self.frame, tearoff=0)
            context_menu.add_command(label="Modify Production", command=self.modify_production)
            context_menu.add_command(label="Delete Production", command=self.delete_production)
            context_menu.add_command(label="Manage Assignment", command=self.manage_assignment)
            context_menu.tk_popup(event.x_root, event.y_root)

    def on_double_click(self, event):
        """Handles double-click event to show production details."""
        selected_item = self.tree.selection()[0]
        production_id = self.tree.item(selected_item)['values'][0]
        self.show_production_details(production_id)

    def open_add_production_window(self):
        """Opens a window to add a new production."""
        ProductionWindow(self.frame, self.session, refresh_callback=self.load_productions)

    def modify_production(self):
        """Opens a window to modify the selected production."""
        selected_item = self.tree.selection()[0]
        production_id = self.tree.item(selected_item)['values'][0]
        ProductionWindow(self.frame, self.session, production_id=production_id, refresh_callback=self.load_productions)

    def delete_production(self):
        """Deletes the selected production from the database."""
        selected_item = self.tree.selection()[0]
        production_id = self.tree.item(selected_item)['values'][0]
        try:
            production = self.session.query(Production).filter_by(production_id=production_id).one()
            self.session.delete(production)
            self.session.commit()
            self.tree.delete(selected_item)
            messagebox.showinfo("Success", "Production deleted successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_production_details(self, production_id):
        """Shows detailed information about the selected production."""
        pass

    def manage_assignment(self):
        """Open the assignment management window for the selected production."""
        selected_item = self.tree.selection()[0]
        production_id = self.tree.item(selected_item)['values'][0]
        AssignmentWindow(self.frame, self.session, production_id)

    def __del__(self):
        """Ensure that the session is closed when the instance is deleted."""
        self.session.close()


import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from db.models import Production, Fund, ShareClass
from config.settings import DATABASE_URL
from utils.Global_Function import populate_combobox

class ProductionWindow:
    def __init__(self, parent, session, production_id=None, refresh_callback=None):
        self.session = session
        self.production_id = production_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Modify Production" if production_id else "Add Production")

        # Create a session if necessary
        self.engine = session.bind
        Session = sessionmaker(bind=self.engine)
        self.local_session = Session()

        # Production Form fields
        self.fund_combobox = self.create_combobox("Fund", Fund, "official_name", "fund_id", on_select=self.on_fund_selected)
        self.share_class_combobox = self.create_combobox("Share Class", ShareClass, "short_name", "share_class_id")

        self.potential_data_source_entry = self.create_form_entry("Potential Data Source")
        self.comment_entry = self.create_form_entry("Comment")
        self.output_file_name_entry = self.create_form_entry("Output File Name")
        self.due_days_entry = self.create_form_entry("Due Days")
        self.production_type_entry = self.create_form_entry("Production Type")
        self.data_point_entry = self.create_form_entry("Data Point")
        self.language_entry = self.create_form_entry("Language")
        self.country_distribution_entry = self.create_form_entry("Country Distribution")
        self.recipient_entry = self.create_form_entry("Recipient")
        self.distribution_mode_entry = self.create_form_entry("Distribution Mode")
        self.data_source_used_entry = self.create_form_entry("Data Source Used")

        # PM Validation Checkbox
        self.pm_validation_var = tk.BooleanVar()  # Create a BooleanVar to store the checkbox value
        self.create_checkbox("PM Validation", self.pm_validation_var)

        # If modifying, load the existing production data into the form fields
        if production_id:
            self.load_production_data()

        # Submit Button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_production)
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

    def create_combobox(self, label_text, model, display_field, value_field, on_select=None):
        """Creates a combobox with values from a table model."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")

        # Create combobox
        combobox = ttk.Combobox(frame)
        populate_combobox(self.local_session, combobox, model, display_field, value_field, on_select=on_select)
        combobox.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)

        return combobox

    def create_checkbox(self, label_text, variable):
        """Creates a checkbox with a label."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")

        # Create the checkbox
        checkbox = tk.Checkbutton(frame, variable=variable)
        checkbox.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)

    def on_fund_selected(self, event):
        """Handles fund selection and populates the share class combobox."""
        selected_fund = self.fund_combobox.get()
        fund_id = int(selected_fund.split(":")[0])  # Extract the fund_id

        # Populate share classes based on the selected fund
        share_classes = self.local_session.query(ShareClass).filter_by(fund_id=fund_id).all()
        share_class_names = [f"{sc.share_class_id}: {sc.short_name}" for sc in share_classes]

        # Add the "None" option at the beginning of the list
        share_class_names.insert(0, "None")

        # Set values in the combobox
        self.share_class_combobox['values'] = share_class_names

        # Set the combobox to "None" by default
        self.share_class_combobox.set("None")

    def load_production_data(self):
        """Load existing production data into the form fields for modification."""
        production = self.session.query(Production).filter_by(production_id=self.production_id).one()

        # Load the fund and share class based on the existing production
        fund = self.session.query(Fund).filter_by(fund_id=production.fund_id).one()
        self.fund_combobox.set(f"{fund.fund_id}: {fund.official_name}")

        # Trigger share class population based on the selected fund
        self.on_fund_selected(None)

        if production.share_class_id:
            # If a share class is selected, set the combobox to the correct share class
            share_class = self.session.query(ShareClass).filter_by(share_class_id=production.share_class_id).one()
            self.share_class_combobox.set(f"{share_class.share_class_id}: {share_class.short_name}")
        else:
            # Add a "None" option if no share class is associated
            current_values = list(self.share_class_combobox['values'])
            if "None" not in current_values:
                self.share_class_combobox['values'] = ["None"] + current_values
            self.share_class_combobox.set("None")

        # Load the PM Validation value
        self.pm_validation_var.set(production.pm_validation)

        # Load other fields
        self.potential_data_source_entry.insert(0, production.potential_data_source)
        self.comment_entry.insert(0, production.comment)
        self.output_file_name_entry.insert(0, production.output_file_name)
        self.due_days_entry.insert(0, production.due_days)
        self.production_type_entry.insert(0, production.production_type)
        self.data_point_entry.insert(0, production.data_point)
        self.language_entry.insert(0, production.language)
        self.country_distribution_entry.insert(0, production.country_distribution)
        self.recipient_entry.insert(0, production.recipient)
        self.distribution_mode_entry.insert(0, production.distribution_mode)
        self.data_source_used_entry.insert(0, production.data_source_used)

    def save_production(self):
        """Saves the production to the database."""
        try:
            selected_fund = self.fund_combobox.get()
            fund_id = int(selected_fund.split(":")[0])  # Extract fund_id

            selected_share_class = self.share_class_combobox.get()
            if selected_share_class and selected_share_class != "None":
                share_class_id = int(selected_share_class.split(":")[0])  # Extract share_class_id
            else:
                share_class_id = None  # Set share_class_id to None if "None" is selected

            if self.production_id:
                # Modify existing production
                production = self.session.query(Production).filter_by(production_id=self.production_id).one()
                production.fund_id = fund_id
                production.share_class_id = share_class_id
                production.potential_data_source = self.potential_data_source_entry.get()
                production.comment = self.comment_entry.get()
                production.output_file_name = self.output_file_name_entry.get()
                production.due_days = self.due_days_entry.get()
                production.production_type = self.production_type_entry.get()
                production.data_point = self.data_point_entry.get()
                production.language = self.language_entry.get()
                production.country_distribution = self.country_distribution_entry.get()
                production.recipient = self.recipient_entry.get()
                production.distribution_mode = self.distribution_mode_entry.get()
                production.data_source_used = self.data_source_used_entry.get()
                production.pm_validation = self.pm_validation_var.get()  # Get checkbox value
            else:
                # Add new production
                production = Production(
                    fund_id=fund_id,
                    share_class_id=share_class_id,
                    potential_data_source=self.potential_data_source_entry.get(),
                    comment=self.comment_entry.get(),
                    output_file_name=self.output_file_name_entry.get(),
                    due_days=self.due_days_entry.get(),
                    production_type=self.production_type_entry.get(),
                    data_point=self.data_point_entry.get(),
                    language=self.language_entry.get(),
                    country_distribution=self.country_distribution_entry.get(),
                    recipient=self.recipient_entry.get(),
                    distribution_mode=self.distribution_mode_entry.get(),
                    data_source_used=self.data_source_used_entry.get(),
                    pm_validation=self.pm_validation_var.get()  # Get checkbox value
                )
                self.session.add(production)

            self.session.commit()
            if self.refresh_callback:
                self.refresh_callback()
            messagebox.showinfo("Success", "Production saved successfully!")
        except SQLAlchemyError as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An error occurred: {e}")






