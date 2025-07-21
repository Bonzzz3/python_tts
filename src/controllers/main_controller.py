import tkinter as tk
from tkinter import ttk, messagebox

from views.main_view import MainNavigationView
from views.widget.status_bar import StatusBar
from controllers.polly_controller import PollyController

class MainController:
    """Main controller for the TTS application navigation and coordination"""
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech App")
        self.root.geometry("800x900")
        
        # Create main container
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create status bar
        self.status_bar = StatusBar(root)
        self.status_bar.pack(fill="x", side="bottom", pady=(0, 0))
        
        # Initialize controllers
        self.polly_controller = PollyController(self.main_frame, self.status_bar, self)
        
        # Always start with navigation screen
        self.show_navigation()

    def show_navigation(self):
        """Show the main navigation screen"""
        self.clear_frame()
        self.navigation_ui = MainNavigationView(self.main_frame, self)
        self.status_bar.update_status("Select a TTS service")

    def navigate_to_polly_interface(self):
        """Handle complete navigation flow to Polly interface"""
        # Disable button if navigation view exists
        if hasattr(self, 'navigation_view') and self.navigation_view.winfo_exists():
            self.navigation_view.polly_btn.config(state=tk.DISABLED)
        
        # Show loading state
        self.update_status("Loading Amazon Polly interface...")
        self.root.update()
        
        # Delegate to polly controller
        self.polly_controller.show_polly_interface()
        
        # Re-enable button if still on navigation view
        if hasattr(self, 'navigation_view') and self.navigation_view.winfo_exists():
            self.navigation_view.polly_btn.config(state=tk.NORMAL)

    def show_placeholder_tts(self):
        """Placeholder for future TTS services"""
        self.status_bar.update_status("Loading other TTS service...")
        self.root.after(1500, lambda: [
            self.status_bar.update_status("Other TTS services coming soon!"),
            messagebox.showinfo("Coming Soon", "Other TTS services will be available in a future update")
        ])

    def update_status(self, message, is_error=False):
        """Update status bar with message"""
        self.status_bar.update_status(message, is_error)

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
