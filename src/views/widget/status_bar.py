import tkinter as tk
from tkinter import ttk

class StatusBar(ttk.Frame):
    """Custom status bar widget"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """Initialize the status bar UI"""
        self.config(relief=tk.SUNKEN)
        
        # Top border line (subtle separator)
        ttk.Separator(self, orient='horizontal').pack(fill="x")

        self.status_label = ttk.Label(
            self,
            text="Ready",
            foreground="white",
            background="#333",
            padding=(10, 5),
            anchor="w",
            font=('Arial', 11)
        )
        self.status_label.pack(fill="x", expand=True)

    def update_status(self, message, is_error=False):
        """Update status bar with message"""
        if is_error:
            self.status_label.config(text=message, foreground="red", background="#333")
        else:
            self.status_label.config(text=message, foreground="green", background="#333")
        self.parent.update_idletasks()