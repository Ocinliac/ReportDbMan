import tkinter as tk
from tkinter import ttk, Menu, messagebox
from sqlalchemy.exc import SQLAlchemyError
from db.setup import engine
from db.models import Production, TechnicalTable, Fund, ShareClass
from gui.modules.data_management_components.production_management.assignment_management import AssignmentWindow
from gui.modules.data_management_components.production_management.people_management import PeopleManagement
from utils.Global_Function import populate_combobox
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(bind=engine))

class ProductionManagement:
    def __init__(self, parent, session):
        self.session = session
        self.parent = parent

        # Create the main frame for the Production Management tab
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        # Create a notebook for sub-tabs inside Production Management
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        # Create sub-tabs for Production and People management
        production_sub_tab = tk.Frame(self.notebook)
        people_sub_tab = tk.Frame(self.notebook)

        # Add sub-tabs to the notebook
        self.notebook.add(production_sub_tab, text="Production")
        self.notebook.add(people_sub_tab, text="People")

        # Initialize sub-tab content
        self.setup_production_ui(production_sub_tab)
        PeopleManagement(people_sub_tab, self.session)  # Initialize PeopleManagement

    def setup_production_ui(self, tab):
        """Set up the user interface for production management."""
        title = tk.Label(tab, text="Production Management", font=("Helvetica", 16))
        title.pack(pady=10)

        # Define columns for the Treeview (removed potential_data_source, comment, data_source_used, and data_point)
        columns = (
            "Production ID", "Fund Name", "Share Class Name", "Output File Name", "Frequency",
            "Due Days", "Production Type", "Language", "Country Distribution", "Recipient",
            "Distribution Mode", "PM Validation"
        )

        # Treeview for displaying production records
        self.tree = ttk.Treeview(tab, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Add Production button
        add_production_button = tk.Button(tab, text="Add Production", command=self.open_add_production_window)
        add_production_button.pack(pady=5)

        # Bind events
        self.tree.bind("<Button-2>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.on_double_click)

        self.load_productions()

    def load_productions(self):
        """Loads productions from the database into the Treeview."""
        # Clear existing entries in the Treeview
        self.tree.delete(*self.tree.get_children())

        try:
            # Query productions along with their related fund and share class
            productions = (
                self.session.query(
                    Production.production_id,
                    Fund.official_name.label("fund_name"),
                    ShareClass.short_name.label("share_class_name"),
                    Production.output_file_name,
                    Production.frequency,
                    Production.due_days,
                    Production.production_type,
                    Production.language,
                    Production.country_distribution,
                    Production.recipient,
                    Production.distribution_mode,
                    Production.pm_validation
                )
                .join(Fund, Production.fund_id == Fund.fund_id, isouter=True)
                .join(ShareClass, Production.share_class_id == ShareClass.share_class_id, isouter=True)
                .all()
            )

            # Insert rows into the Treeview
            for production in productions:
                self.tree.insert(
                    "", "end",
                    values=(
                        production.production_id,
                        production.fund_name or "N/A",  # Display "N/A" if no fund is associated
                        production.share_class_name or "None",  # Display "None" if no share class is associated
                        production.output_file_name,
                        production.frequency,
                        production.due_days,
                        production.production_type,
                        production.language,
                        production.country_distribution,
                        production.recipient,
                        production.distribution_mode,
                        production.pm_validation
                    )
                )
        except SQLAlchemyError as e:
            messagebox.showerror("Error", f"An error occurred while loading productions: {e}")

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
        self.modify_production(production_id)

    def open_add_production_window(self):
        """Opens a window to add a new production."""
        ProductionWindow(self.frame, self.session, refresh_callback=self.load_productions)

    def modify_production(self, production_id=None):
        """Opens a window to modify the selected production."""
        if not production_id:
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

    def manage_assignment(self):
        """Open the assignment management window for the selected production."""
        selected_item = self.tree.selection()[0]
        production_id = self.tree.item(selected_item)['values'][0]
        AssignmentWindow(self.frame, self.session, production_id)


class ProductionWindow:
    def __init__(self, parent, session, production_id=None, refresh_callback=None):
        self.session = session
        self.production_id = production_id
        self.refresh_callback = refresh_callback
        self.window = tk.Toplevel(parent)
        self.window.title("Modify Production" if production_id else "Add Production")

        # Create form fields
        self.fund_combobox = self.create_combobox("Fund", Fund, "official_name", "fund_id", self.on_fund_selected)
        self.fund_combobox.bind("<<ComboboxSelected>>", self.on_fund_selected)
        self.share_class_combobox = self.create_combobox("Share Class", ShareClass, "short_name", "share_class_id")

        # Frequency combobox (filtered by tt_category = "Frequency")
        self.frequency_combobox = self.create_combobox(
            "Frequency", TechnicalTable, "tt_value", "tt_id",
            filter_by={"tt_category": "Frequency"}, display_format="display_only"
        )

        # Language combobox (filtered by tt_category = "Language")
        self.language_combobox = self.create_combobox(
            "Language", TechnicalTable, "tt_value", "tt_id",
            filter_by={"tt_category": "Language"}, display_format="display_only"
        )

        # Distribution Mode combobox (filtered by tt_category = "Distribution mode")
        self.distribution_mode_combobox = self.create_combobox(
            "Distribution Mode", TechnicalTable, "tt_value", "tt_id",
            filter_by={"tt_category": "Distribution mode"}, display_format="display_only"
        )

        # Production Type combobox (filtered by tt_category = "Production type")
        self.production_type_combobox = self.create_combobox(
            "Production Type", TechnicalTable, "tt_value", "tt_id",
            filter_by={"tt_category": "Production type"}, display_format="display_only"
        )

        # Country Distribution combobox (filtered by tt_category = "Country")
        self.country_distribution_combobox = self.create_combobox(
            "Country Distribution", TechnicalTable, "tt_value", "tt_id",
            filter_by={"tt_category": "Country"}, display_format="display_only"
        )

        # Other form fields
        self.output_file_name_entry = self.create_form_entry("Output File Name")
        self.due_days_entry = self.create_form_entry("Due Days")
        self.create_form_entry("Client Type")
        self.create_form_entry("Days of the Week")
        self.recipient_entry = self.create_form_entry("Recipient")

        # PM Validation Checkbox
        self.pm_validation_var = tk.BooleanVar()
        self.create_checkbox("PM Validation", self.pm_validation_var)

        # If modifying, load existing production data
        if production_id:
            self.load_production_data()

        # Submit button
        submit_button = tk.Button(self.window, text="Submit", command=self.save_production)
        submit_button.pack(pady=20)

    def create_form_entry(self, label_text):
        """Helper function to create a labeled entry field."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        entry = tk.Entry(frame)
        entry.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)
        return entry

    def create_combobox(self, label_text, model, display_field, value_field, filter_by=None, on_select=None,
                        display_format="both"):
        """Helper function to create a labeled combobox with an optional display format."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        combobox = ttk.Combobox(frame)
        populate_combobox(self.session, combobox, model, display_field, value_field, filter_by=filter_by,
                          on_select=on_select, display_format=display_format)
        combobox.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)
        return combobox

    def create_checkbox(self, label_text, variable):
        """Helper function to create a labeled checkbox."""
        frame = tk.Frame(self.window)
        label = tk.Label(frame, text=label_text)
        label.pack(side="left")
        checkbox = tk.Checkbutton(frame, variable=variable)
        checkbox.pack(side="right", fill="x", expand=True)
        frame.pack(fill="x", pady=5)

    def on_fund_selected(self, event):
        """Handle fund selection to update share class combobox."""
        selected_fund = self.fund_combobox.get()
        fund_id = int(selected_fund.split(":")[0])
        share_classes = self.session.query(ShareClass).filter_by(fund_id=fund_id).all()
        self.share_class_combobox['values'] = ["None"] + [f"{sc.share_class_id}: {sc.short_name}" for sc in
                                                          share_classes]
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
            self.share_class_combobox.set("None")

        # Load the PM Validation value
        self.pm_validation_var.set(production.pm_validation)

        # Load other fields
        self.output_file_name_entry.insert(0, production.output_file_name or "")
        self.due_days_entry.insert(0, production.due_days or "")
        self.recipient_entry.insert(0, production.recipient or "")

        # Use the helper function to load values into the comboboxes
        self.set_combobox_value(self.frequency_combobox, production.frequency)
        self.set_combobox_value(self.language_combobox, production.language)
        self.set_combobox_value(self.distribution_mode_combobox, production.distribution_mode)
        self.set_combobox_value(self.production_type_combobox, production.production_type)
        self.set_combobox_value(self.country_distribution_combobox, production.country_distribution)

    def set_combobox_value(self, combobox, value):
        """Helper function to set the value of a combobox if the value is available."""
        available_values = combobox['values']
        if value and value in available_values:
            combobox.set(value)
        else:
            combobox.set("None")  # Optional: Set to "None" or default if the value is not found

    def save_production(self):
        """Save production details to the database."""
        session = Session()  # Create a new session for saving
        try:
            selected_fund = self.fund_combobox.get()
            fund_id = int(selected_fund.split(":")[0])
            share_class_id = int(
                self.share_class_combobox.get().split(":")[0]) if self.share_class_combobox.get() != "None" else None

            if self.production_id:
                production = session.query(Production).filter_by(production_id=self.production_id).one()
            else:
                production = Production()

            # Set production data from form inputs
            production.fund_id = fund_id
            production.share_class_id = share_class_id
            production.frequency = self.frequency_combobox.get()
            production.language = self.language_combobox.get()
            production.output_file_name = self.output_file_name_entry.get()
            production.due_days = self.due_days_entry.get()
            production.recipient = self.recipient_entry.get()
            production.pm_validation = self.pm_validation_var.get()

            # Set additional combobox values
            production.distribution_mode = self.distribution_mode_combobox.get()
            production.production_type = self.production_type_combobox.get()
            production.country_distribution = self.country_distribution_combobox.get()

            # Add new production or update existing
            if not self.production_id:
                session.add(production)

            session.commit()  # Commit changes to the database
            if self.refresh_callback:
                self.refresh_callback()
            messagebox.showinfo("Success", "Production saved successfully!")
            self.window.destroy()  # Close the window after saving
        except SQLAlchemyError as e:
            session.rollback()  # Rollback in case of an error
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            session.close()  # Close session after transaction

