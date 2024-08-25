# gui/modules/data_management/code_management.py

class CodeManagement:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        # Set up code management UI here
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface for code management."""
        title = tk.Label(self.frame, text="Code Management", font=("Helvetica", 16))
        title.pack(pady=10)

        # Similar to FundManagement, add buttons for adding, modifying, and removing codes
