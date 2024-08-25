# gui/modules/data_management.py

import tkinter as tk
from tkinter import ttk
from gui.modules.data_management_components.fund_management import FundManagement
# We won't directly instantiate these here:
# from gui.modules.data_management_components.code_management import FundCodesWindow
# from gui.modules.data_management_components.share_class_management import ShareClassWindow

class DataManagement:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        # Create tabs for different data management functionalities
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True)

        # Create tabs
        fund_tab = tk.Frame(notebook)


        # Add tabs to the notebook
        notebook.add(fund_tab, text="Funds")

        # Initialize Fund Management tab
        FundManagement(fund_tab)


