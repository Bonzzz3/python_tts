import tkinter as tk
from tkinter import ttk

class MainNavigationView(ttk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.polly_btn = None
        self.azure_btn = None
        self.setup_ui()

    def setup_ui(self):
        """Initialize the navigation UI"""
        self.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Title
        ttk.Label(self, text="Text-to-Speech Services", font=('Arial', 16, 'bold')).pack(pady=20)
        
        # Amazon Polly Button
        self.polly_btn = ttk.Button(
            self,
            text="Amazon Polly TTS",
            command=self.controller.navigate_to_polly_interface,
            width=20
        )
        self.polly_btn.pack(pady=15)
        
        # Azure Speech Services Button
        self.azure_btn = ttk.Button(
            self,
            text="Azure Speech Services",
            command=self.controller.navigate_to_azure_interface,
            width=20
        )
        self.azure_btn.pack(pady=15)
        
        # Other TTS Button
        ttk.Button(
            self,
            text="Other TTS (Coming Soon)",
            command=lambda: self.controller.status_bar.update_status("Other TTS services coming soon!"),
            width=20
        ).pack(pady=15)