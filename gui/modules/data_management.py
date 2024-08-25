# gui/modules/data_management.py

import tkinter as tk
from tkinter import ttk
from gui.modules.data_management_components.fund_management import FundManagement
from gui.modules.data_management_components.code_management import CodeManagement
from gui.modules.data_management_components.share_class_management import ShareClassManagement


class DataManagement:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        # Create tabs for different data management functionalities
        notebook = ttk.Notebook(self.frame)
        notebook.pack(fill="both", expand=True)

        fund_tab = tk.Frame(notebook)
        code_tab = tk.Frame(notebook)
        share_class_tab = tk.Frame(notebook)

        notebook.add(fund_tab, text="Funds")
        notebook.add(code_tab, text="Codes")
        notebook.add(share_class_tab, text="Share Classes")

        FundManagement(fund_tab)
        CodeManagement(code_tab)
        ShareClassManagement(share_class_tab)
