# gui/modules/data_management_components/common_widget.py

import tkinter as tk

def create_form_entry(parent, label_text, initial_value=None, readonly=False):
    """Creates a label and entry field for a form."""
    frame = tk.Frame(parent)
    label = tk.Label(frame, text=label_text)
    label.pack(side="left", padx=5)
    entry = tk.Entry(frame)
    if initial_value:
        entry.insert(0, initial_value)
    if readonly:
        entry.config(state='readonly')
    entry.pack(side="right", fill="x", expand=True)
    frame.pack(fill="x", pady=5)
    return entry

def create_button(parent, text, command):
    """Creates a standard button."""
    button = tk.Button(parent, text=text, command=command)
    button.pack(pady=10)
    return button
