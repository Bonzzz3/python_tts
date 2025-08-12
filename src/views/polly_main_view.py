import tkinter as tk
from tkinter import scrolledtext, ttk

class PollyMainView(ttk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        """Initialize the main UI"""
        self.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Top navigation frame
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", pady=5)
        
        # Back button
        ttk.Button(nav_frame, text="← Back to Menu", 
                  command=self.controller.show_navigation, width=15).pack(side="left", padx=5)
        
        # AWS Configuration Frame
        config_frame = ttk.LabelFrame(self, text="AWS Configuration", padding=10)
        config_frame.pack(fill="x", pady=5)
        
        # Region Selection
        ttk.Label(config_frame, text="AWS Region:").grid(row=0, column=0, sticky="w")
        self.region_dropdown = ttk.Combobox(config_frame, 
                                          textvariable=self.controller.region_var, 
                                          state="readonly")
        self.region_dropdown.grid(row=0, column=1, sticky="ew", padx=5)
        self.region_dropdown.bind("<<ComboboxSelected>>", 
                                 self.controller.update_engines_for_region)
        
        # Edit Credentials Button
        ttk.Button(config_frame, text="Edit Credentials", 
                  command=self.controller._show_polly_auth_interface,
                  width=15).grid(row=0, column=2, padx=5)
        
        config_frame.grid_columnconfigure(1, weight=1)

        # Text Input Frame
        text_frame = ttk.LabelFrame(self, text="Text to Convert", padding=10)
        text_frame.pack(fill="both", expand=True, pady=5)
        
        # Text Input
        ttk.Label(text_frame, text="Enter Text:").pack(anchor="w")
        self.text_input = scrolledtext.ScrolledText(text_frame, width=60, height=5)
        self.text_input.pack(fill="both", expand=True, pady=5)
        self.text_input.bind("<KeyRelease>", self.controller.update_char_count)
        
        # Character count display
        count_frame = ttk.Frame(text_frame)
        count_frame.pack(fill="x", pady=5)
        ttk.Label(count_frame, text="Character Count:").pack(side="left")
        self.char_count_label = ttk.Label(count_frame, textvariable=self.controller.char_count_var)
        self.char_count_label.pack(side="left")
        
        # Voice Engine Selection
        engine_frame = ttk.Frame(text_frame)
        engine_frame.pack(fill="x", pady=5)
        ttk.Label(engine_frame, text="Voice Engine:").pack(side="left")
        self.engine_dropdown = ttk.Combobox(engine_frame, 
                                          textvariable=self.controller.engine_var, 
                                          state="readonly", width=15)
        self.engine_dropdown.pack(side="left", padx=5)
        self.engine_dropdown.bind("<<ComboboxSelected>>", self.controller.update_output_formats)
        
        # Language Selection
        ttk.Label(text_frame, text="Language:").pack(anchor="w", pady=(10, 0))
        self.language_dropdown = ttk.Combobox(text_frame, 
                                            textvariable=self.controller.language_var, 
                                            state="readonly")
        self.language_dropdown.pack(fill="x", pady=5)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.controller.on_language_changed)
        
        # Gender Filter Selection
        ttk.Label(text_frame, text="Gender:").pack(anchor="w")
        self.gender_dropdown = ttk.Combobox(text_frame, 
                                          textvariable=self.controller.gender_var, 
                                          values=["All", "Male", "Female"],
                                          state="readonly")
        self.gender_dropdown.pack(fill="x", pady=5)
        self.gender_dropdown.bind("<<ComboboxSelected>>", self.controller.update_gender_filter)
        
        # Voice Selection
        ttk.Label(text_frame, text="Voice:").pack(anchor="w")
        self.voice_dropdown = ttk.Combobox(text_frame, 
                                          textvariable=self.controller.voice_var, 
                                          state="readonly")
        self.voice_dropdown.pack(fill="x", pady=5)
        
        # Output Format Selection
        ttk.Label(text_frame, text="Output Format:").pack(anchor="w", pady=(10, 0))
        self.format_dropdown = ttk.Combobox(text_frame, 
                                          textvariable=self.controller.output_format_var, 
                                          state="readonly")
        self.format_dropdown.pack(fill="x", pady=5)
        self.format_dropdown.bind("<<ComboboxSelected>>", self.controller.update_sample_rates)
        
        # Sample Rate Selection
        ttk.Label(text_frame, text="Sample Rate (Hz):").pack(anchor="w")
        self.sample_rate_dropdown = ttk.Combobox(text_frame, 
                                               textvariable=self.controller.sample_rate_var, 
                                               state="readonly")
        self.sample_rate_dropdown.pack(fill="x", pady=5)

        # Action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Generate & Play", 
                  command=self.controller.play_audio_directly).pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="Generate & Save", 
                  command=self.controller.generate).pack(side='left', padx=5)
