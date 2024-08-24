import tkinter as tk


class DataManagement:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg="#ecf0f1")
        self.frame.pack(fill="both", expand=True)

        label = tk.Label(self.frame, text="Data Management", font=("Helvetica", 16))
        label.pack(pady=20)
