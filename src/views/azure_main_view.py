import tkinter as tk
from tkinter import scrolledtext, ttk

class AzureMainView(ttk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """Initialize the main UI"""
        self.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top navigation frame
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill="x", pady=5)
        
        # Back button
        self.back_btn = ttk.Button(
            self.nav_frame,
            text="← Back to Menu",
            command=self.controller.show_navigation,
            width=15
        )
        self.back_btn.pack(side="left", padx=5)
        
        # Edit Credentials Button
        ttk.Button(self.nav_frame, text="Edit Credentials", 
                  command=self.controller._show_azure_auth_interface,
                  width=15).pack(side="right", padx=5)
        
        # Configure grid weights
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        # Text Input Frame
        text_frame = ttk.LabelFrame(self, text="Text to Convert", padding=10)
        text_frame.pack(fill="both", expand=True, pady=5)
        
        # Text Input
        ttk.Label(text_frame, text="Enter Text:").pack(anchor="w")
        self.text_input = scrolledtext.ScrolledText(text_frame, width=60, height=10)
        self.text_input.pack(fill="both", expand=True, pady=5)
        
        # Character count display
        count_frame = ttk.Frame(text_frame)
        count_frame.pack(fill="x", pady=5)
        ttk.Label(count_frame, text="Character Count:").pack(side="left")
        self.char_count_label = ttk.Label(count_frame, 
                                        textvariable=self.controller.char_count_var)
        self.char_count_label.pack(side="left")
        self.text_input.bind("<KeyRelease>", self.controller.update_char_count)

        # Language Selection
        ttk.Label(text_frame, text="Language:").pack(anchor="w")
        self.language_dropdown = ttk.Combobox(text_frame, 
                                            textvariable=self.controller.language_var, 
                                            state="readonly")
        self.language_dropdown.pack(fill="x", pady=5)
        self.language_dropdown.bind("<<ComboboxSelected>>", 
                                   self._on_language_changed)
        
        # Gender Filter Selection
        ttk.Label(text_frame, text="Gender:").pack(anchor="w")
        self.gender_dropdown = ttk.Combobox(text_frame, 
                                          textvariable=self.controller.gender_var, 
                                          values=["All", "Male", "Female"],
                                          state="readonly")
        self.gender_dropdown.pack(fill="x", pady=5)
        self.gender_dropdown.bind("<<ComboboxSelected>>", 
                                 self.controller.update_gender_filter)
        
        # Voice Selection
        ttk.Label(text_frame, text="Voice:").pack(anchor="w")
        self.voice_dropdown = ttk.Combobox(text_frame, 
                                          textvariable=self.controller.voice_var, 
                                          state="readonly")
        self.voice_dropdown.pack(fill="x", pady=5)
        
        # Generate and Play/Save Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Generate & Play",
            command=self.controller.play_audio_directly
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Generate & Save",
            command=self.controller.generate_and_save
        ).pack(side='left', padx=5)

    def _on_language_changed(self, event=None):
        """Handle language change event"""
        # Update available genders for the selected language
        selected_lang = self.controller.language_var.get()
        if selected_lang:
            available_genders = self.controller.get_available_genders_for_language(selected_lang)
            self.gender_dropdown['values'] = available_genders
            
            # Reset gender filter to "All" when language changes
            self.controller.gender_var.set("All")
        
        # Update voices for the new language
        self.controller.update_voices()

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.winfo_children():
            widget.destroy()
        self.controller.char_count_var.set("0/3000")
