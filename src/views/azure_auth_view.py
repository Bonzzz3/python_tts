from tkinter import ttk
import tkinter as tk

class AzureAuthView(ttk.Frame):
    """UI for entering Azure Speech Services credentials"""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.remember_var = tk.BooleanVar()
        self.setup_ui()

    def setup_ui(self):
        """Initialize the credentials UI"""
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ttk.Label(self, text="Azure Speech Services Configuration", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Subscription Key
        ttk.Label(self, text="Subscription Key:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Entry(self, textvariable=self.controller.api_key_var, width=50, show="*").pack(fill="x", pady=5)
        
        # Endpoint
        ttk.Label(self, text="Endpoint:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        ttk.Entry(self, textvariable=self.controller.endpoint_var, width=50).pack(fill="x", pady=5)
        
        # Remember me checkbox
        ttk.Checkbutton(self, text="Remember me", variable=self.remember_var).pack(anchor="w", pady=10)
        
        # Info text
        info_text = ttk.Label(self, 
                             text="Get your Azure Speech Services credentials from the Azure portal.\n"
                                  "Create a Speech service resource and copy the key and endpoint.",
                             foreground="gray")
        info_text.pack(pady=10)
        
        # Buttons frame
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)
        
        # Connect button
        ttk.Button(button_frame, text="Connect", 
                  command=self.controller.verify_and_continue,
                  style='Accent.TButton').pack(side="left", padx=5)
