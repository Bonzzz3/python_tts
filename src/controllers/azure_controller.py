import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox
from views.azure_main_view import AzureMainView
from views.azure_auth_view import AzureAuthView
from managers.azure_auth_manager import AzureAuthenticationManager
from managers.azure_speech_manager import AzureSpeechManager

class AzureController:
    """Controller for Azure TTS functionality"""
    def __init__(self, main_frame, status_bar, main_controller=None):
        self.main_frame = main_frame
        self.status_bar = status_bar
        self.main_controller = main_controller
        
        # Initialize variables
        self.api_key_var = tk.StringVar()
        self.endpoint_var = tk.StringVar()
        self.language_var = tk.StringVar()
        self.voice_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="All")
        self.char_count_var = tk.StringVar(value="0/3000")
        self.remaining_chars = 3000
        
        # Initialize authentication manager
        self.auth_manager = AzureAuthenticationManager(self.api_key_var, self.endpoint_var)
        
        # Initialize TTS manager
        self.tts_manager = AzureSpeechManager()
        
        # Try to load saved credentials
        self.auth_manager.load_credentials()
        
        # Dynamic voice data will be managed by TTS manager
        self.voices_loaded = False

    def show_navigation(self):
        """Navigate back to main navigation screen"""
        if self.main_controller:
            self.main_controller.show_navigation()
        else:
            self.update_status("Navigation not available", is_error=True)

    def show_azure_interface(self):
        """Show the Azure TTS interface"""
        if self.api_key_var.get() and self.endpoint_var.get():
            self._show_azure_main_interface()
        else:
            self._show_azure_auth_interface()

    def _show_azure_main_interface(self):
        """Show the main Azure TTS interface"""
        self.clear_frame()
        self.azure_ui = AzureMainView(self.main_frame, self)
        self.update_languages()
        self.status_bar.update_status("Azure Speech Services ready")

    def _show_azure_auth_interface(self):
        """Show the Azure authentication interface"""
        self.clear_frame()
        self.azure_auth_ui = AzureAuthView(self.main_frame, self)
        
        # Load the remember preference if credentials were previously saved
        if self.auth_manager.has_saved_credentials():
            self.azure_auth_ui.remember_var.set(True)
        
        self.status_bar.update_status("Enter Azure credentials")

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.char_count_var.set("0/3000")

    def update_char_count(self, event=None):
        """Update character count display"""
        if hasattr(self, 'azure_ui'):
            text = self.azure_ui.text_input.get("1.0", tk.END)
            char_count = len(text.strip())
            remaining = max(0, self.remaining_chars - char_count)
            self.char_count_var.set(f"{char_count}/{self.remaining_chars}")
            if remaining < 100:
                self.azure_ui.char_count_label.config(foreground="red")

    def fetch_available_voices(self):
        """Fetch available voices using Azure TTS Manager"""
        try:
            if not self.api_key_var.get() or not self.endpoint_var.get():
                self.update_status("API credentials required to fetch voices", is_error=True)
                return False
            
            self.update_status("Fetching available voices...")
            self.main_frame.master.update()
            
            # Use TTS manager to fetch voices
            success, message = self.tts_manager.fetch_available_voices(
                self.api_key_var.get(),
                self.endpoint_var.get()
            )
            
            if success:
                self.voices_loaded = True
                self.update_status(message)
                return True
            else:
                self.update_status(message, is_error=True)
                return False
                
        except Exception as e:
            self.update_status(f"Error fetching voices: {str(e)}", is_error=True)
            return False

    def update_languages(self, event=None):
        """Update available languages"""
        try:
            if not self.voices_loaded:
                # Try to fetch voices if not already loaded
                if not self.fetch_available_voices():
                    # If fetching fails, show error and return
                    if hasattr(self, 'azure_ui'):
                        self.azure_ui.language_dropdown['values'] = []
                        self.azure_ui.voice_dropdown['values'] = []
                    return
            
            # Get list of available languages from TTS manager
            languages = self.tts_manager.get_languages()
            
            if hasattr(self, 'azure_ui'):
                self.azure_ui.language_dropdown['values'] = languages
                
                if languages:
                    # Set default to en-US if available, otherwise first language
                    default_lang = next((lang for lang in languages if 'English (United States)' in lang), languages[0])
                    self.language_var.set(default_lang)
                    self.update_voices()
                
            self.update_status(f"Loaded {len(languages)} languages")
            
        except Exception as e:
            self.update_status(f"Error updating languages: {str(e)}", is_error=True)

    def update_voices(self, event=None):
        """Update available voices based on selected language and gender filter"""
        try:
            selected_lang = self.language_var.get()
            selected_gender = self.gender_var.get()
            
            if not selected_lang:
                if hasattr(self, 'azure_ui'):
                    self.azure_ui.voice_dropdown['values'] = []
                return
                
            # Get voices for selected language from TTS manager
            voice_displays = self.tts_manager.get_voices_for_language(selected_lang)
            
            # Filter by gender if not "All"
            if selected_gender != "All":
                filtered_voices = []
                for voice_display in voice_displays:
                    voice_short_name = self.tts_manager.get_voice_short_name(voice_display, selected_lang)
                    voice_gender = self.tts_manager.get_voice_gender(voice_short_name)
                    if voice_gender and voice_gender.lower() == selected_gender.lower():
                        filtered_voices.append(voice_display)
                voice_displays = filtered_voices
            
            if hasattr(self, 'azure_ui'):
                self.azure_ui.voice_dropdown['values'] = voice_displays
            
            if voice_displays:
                self.voice_var.set(voice_displays[0])
            else:
                self.voice_var.set("")
                
            gender_text = f" ({selected_gender})" if selected_gender != "All" else ""
            self.update_status(f"Loaded {len(voice_displays)} voices for {selected_lang}{gender_text}")
            
        except Exception as e:
            self.update_status(f"Error updating voices: {str(e)}", is_error=True)

    def update_gender_filter(self, event=None):
        """Update voices when gender filter changes"""
        self.update_voices()

    def get_available_genders_for_language(self, language):
        """Get available genders for a specific language"""
        try:
            return self.tts_manager.get_available_genders_for_language(language)
        except Exception as e:
            print(f"Error getting genders for language: {e}")
            return ["All", "Male", "Female"]

    def _get_voice_short_name(self, voice_display):
        """Get the actual voice short name from the display name"""
        selected_lang = self.language_var.get()
        return self.tts_manager.get_voice_short_name(voice_display, selected_lang)

    def verify_and_continue(self):
        """Verify Azure credentials and continue"""
        api_key = self.api_key_var.get().strip()
        endpoint = self.endpoint_var.get().strip()
        
        if not api_key or not endpoint:
            self.update_status("Both API Key and Endpoint are required", is_error=True)
            messagebox.showerror("Error", "Both Subscription Key and Endpoint are required")
            return
        
        try:
            self.update_status("Verifying Azure credentials...")
            self.main_frame.master.update()
            
            if self.tts_manager.test_credentials(api_key, endpoint):
                self.update_status("Credentials verified successfully!")
                
                # Save credentials if remember me is checked
                if hasattr(self, 'azure_auth_ui'):
                    remember = self.azure_auth_ui.remember_var.get()
                    self.auth_manager.save_credentials(remember)
                
                self._show_azure_main_interface()
            else:
                raise Exception("Authentication failed")
            
        except Exception as e:
            error_msg = str(e)
            self.update_status(f"Verification failed: {error_msg}", is_error=True)
            messagebox.showerror("Azure Error", f"Invalid credentials: {error_msg}")

    def _validate_synthesis_inputs(self):
        """Validate inputs for synthesis"""
        if not hasattr(self, 'azure_ui'):
            self.update_status("UI not initialized.", is_error=True)
            return None
            
        text = self.azure_ui.text_input.get("1.0", tk.END).strip()
        
        if not text:
            self.update_status("Please enter text.", is_error=True)
            return None
        
        if not self.api_key_var.get() or not self.endpoint_var.get():
            self.update_status("Azure configuration is incomplete.", is_error=True)
            return None
            
        if not self.voice_var.get():
            self.update_status("Please select a voice.", is_error=True)
            return None
        
        return text

    def generate_and_save(self):
        """Generate speech and save to file"""
        text = self._validate_synthesis_inputs()
        if not text:
            return
        
        try:
            self.update_status("Generating audio...")
            self.main_frame.master.update()
            
            voice_short_name = self._get_voice_short_name(self.voice_var.get())
            output_path = self.tts_manager.generate_output_filename(voice_short_name)
            
            success, message = self.tts_manager.synthesize_to_file(
                text,
                self.api_key_var.get(),
                self.endpoint_var.get(),
                voice_short_name,
                output_path
            )
            
            if success:
                self.update_status(message)
                self._open_file_location(output_path)
            else:
                self.update_status(message, is_error=True)
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}", is_error=True)

    def play_audio_directly(self):
        """Generate and play audio without saving"""
        text = self._validate_synthesis_inputs()
        if not text:
            return
        
        try:
            self.update_status("Generating and playing...")
            self.main_frame.master.update()
            
            voice_short_name = self._get_voice_short_name(self.voice_var.get())
            
            success, tmp_path, message = self.tts_manager.synthesize_to_temp_file(
                text,
                self.api_key_var.get(),
                self.endpoint_var.get(),
                voice_short_name
            )
            
            if success:
                self._play_audio_file(tmp_path)
                self.update_status("Audio played successfully")
            else:
                self.update_status(message, is_error=True)
                
        except Exception as e:
            self.update_status(f"Playback error: {str(e)}", is_error=True)

    def _open_file_location(self, file_path):
        """Open file location in system file manager"""
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", "-R", file_path])
        elif system == "Windows":
            subprocess.run(["explorer", "/select,", file_path])
        elif system == "Linux":
            subprocess.run(["xdg-open", os.path.dirname(file_path)])

    def _play_audio_file(self, file_path):
        """Play audio file using system player"""
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                subprocess.run(["afplay", file_path])
            elif system == "Windows":
                subprocess.run(["start", file_path], shell=True)
            elif system == "Linux":
                subprocess.run(["aplay", file_path])
        finally:
            # Clean up temp file
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def update_status(self, message, is_error=False):
        """Update status bar with message"""
        self.status_bar.update_status(message, is_error)

    def clear_saved_credentials(self):
        """Clear saved Azure credentials"""
        try:
            if self.auth_manager.clear_credentials():
                self.api_key_var.set('')
                self.endpoint_var.set('')
                self.update_status("Saved credentials cleared successfully")
                messagebox.showinfo("Success", "Saved credentials have been cleared.")
            else:
                self.update_status("Failed to clear credentials", is_error=True)
                messagebox.showerror("Error", "Failed to clear saved credentials.")
        except Exception as e:
            self.update_status(f"Error clearing credentials: {str(e)}", is_error=True)
            messagebox.showerror("Error", f"Error clearing credentials: {str(e)}")
