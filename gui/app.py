# gui/app.py

import tkinter as tk
from tkinter import ttk
from gui.modules.production_management import ProductionManagement
from gui.modules.data_management import DataManagement

# from gui.modules.reporting_analytics import ReportingAnalytics
# from gui.modules.incident_management import IncidentManagement


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Fund Management Application")
        self.geometry("1200x800")

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#2c3e50", width=200, height=800)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        self.add_sidebar_buttons()

        # Main content area
        self.main_content = tk.Frame(self, bg="#ecf0f1")
        self.main_content.grid(row=0, column=1, sticky="nsew")

        # Status bar (optional)
        self.status_bar = tk.Label(self, text="Status: Ready", bg="#2c3e50", fg="white")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

    def add_sidebar_buttons(self):
        """Create buttons for the sidebar."""
        buttons = [
            ("Production Management", self.show_production_management),
            ("Data Management", self.show_data_management),
            ("Reporting & Analytics", self.show_reporting_analytics),
            ("Incident Management & Support", self.show_incident_management),
        ]

        for idx, (text, command) in enumerate(buttons):
            button = tk.Button(
                self.sidebar, text=text, command=command, bg="#34495e", fg="white",
                bd=0, highlightthickness=0, relief="flat", height=2
            )
            button.pack(fill="x", pady=10, padx=10)

    def clear_main_content(self):
        """Clears the main content area."""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_production_management(self):
        """Display the Production Management module."""
        self.clear_main_content()
        ProductionManagement(self.main_content)

    def show_data_management(self):
        """Display the Data Management module."""
        self.clear_main_content()
        DataManagement(self.main_content)

    def show_reporting_analytics(self):
        """Display the Reporting & Analytics module."""
        self.clear_main_content()
        ReportingAnalytics(self.main_content)

    def show_incident_management(self):
        """Display the Incident Management & Support module."""
        self.clear_main_content()
        IncidentManagement(self.main_content)


if __name__ == "__main__":
    app = App()
    app.mainloop()
