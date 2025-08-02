from tkinter import ttk

class PollyAuthenticationView(ttk.Frame):
    """UI for entering AWS credentials"""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """Initialize the credentials UI"""
        self.pack(fill="both", expand=True, padx=20, pady=20)
        
        ttk.Label(self, text="AWS Credentials Setup", font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Access Key
        ttk.Label(self, text="AWS Access Key ID:").pack(anchor="w")
        ttk.Entry(self, textvariable=self.controller.access_key_var, width=40).pack(fill="x", pady=5)
        
        # Secret Key
        ttk.Label(self, text="AWS Secret Access Key:").pack(anchor="w")
        ttk.Entry(self, textvariable=self.controller.secret_key_var, width=40, show="*").pack(fill="x", pady=5)
        
        # Remember checkbox
        ttk.Checkbutton(self, text="Remember credentials", 
                        variable=self.controller.remember_var).pack(pady=10)
        
        # Submit Button
        ttk.Button(self, text="Save & Continue", 
                  command=self.controller.verify_and_continue).pack(pady=20)

