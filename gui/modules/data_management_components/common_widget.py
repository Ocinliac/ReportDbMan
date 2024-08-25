# gui/modules/data_management/common_widgets.py

import tkinter as tk
from tkinter import ttk

def create_form_entry(parent, label_text):
    """Creates a label and entry field for a form."""
    frame = tk.Frame(parent)
    label = tk.Label(frame, text=label_text)
    label.pack(side="left")
    entry = tk.Entry(frame)
    entry.pack(side="right", fill="x", expand=True)
    frame.pack(fill="x", pady=5)
    return entry
