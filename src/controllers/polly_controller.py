import subprocess
import platform
import tempfile
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os

from managers.aws_auth_manager import AWSAuthenticationManager
from managers.aws_polly_manager import AWSPollyManager
from views.polly_auth_view import PollyAuthenticationView
from views.polly_main_view import PollyMainView

class PollyController:
    """Controller for Amazon Polly TTS functionality"""
    def __init__(self, main_frame, status_bar, main_controller=None):
        self.main_frame = main_frame
        self.status_bar = status_bar
        self.main_controller = main_controller
        
        # Initialize variables
        self.access_key_var = tk.StringVar()
        self.secret_key_var = tk.StringVar()
        self.region_var = tk.StringVar()
        self.engine_var = tk.StringVar(value="neural")
        self.language_var = tk.StringVar()
        self.voice_var = tk.StringVar()
        self.gender_var = tk.StringVar(value="All")
        self.output_format_var = tk.StringVar(value="mp3")
        self.sample_rate_var = tk.StringVar(value="22050")
        self.remember_var = tk.IntVar(value=1)
        self.char_count_var = tk.StringVar(value="0/3000")
        self.remaining_chars = 3000
        
        # Initialize managers
        self.credentials_manager = AWSAuthenticationManager(self.access_key_var, self.secret_key_var)
        self.polly_manager = AWSPollyManager(self.access_key_var, self.secret_key_var)
        
        # Check for saved credentials
        self.credentials_manager.load_credentials()

    def show_navigation(self):
        """Navigate back to main navigation screen"""
        if self.main_controller:
            self.main_controller.show_navigation()
        else:
            self.update_status("Navigation not available", is_error=True)

    def show_polly_interface(self):
        """Determine and show the appropriate Polly interface view"""
        if self.access_key_var.get() and self.secret_key_var.get():
            self._show_polly_main_interface()
        else:
            self._show_polly_auth_interface()

    def _show_polly_main_interface(self):
        """Show the main Polly TTS interface"""
        self.clear_frame()
        self.main_ui = PollyMainView(self.main_frame, self)
        self.load_regions()
        self.char_count_var.set("0/3000")
        self.status_bar.update_status("Amazon Polly ready")

    def _show_polly_auth_interface(self):
        """Show the Polly authentication interface"""
        self.clear_frame()
        self.credentials_ui = PollyAuthenticationView(self.main_frame, self)
        self.status_bar.update_status("Enter AWS credentials")

    def clear_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.char_count_var.set("0/3000")

    def update_char_count(self, event=None):
        """Update character count display"""
        text = self.text_input.get("1.0", tk.END)
        char_count = len(text.strip())
        remaining = max(0, self.remaining_chars - char_count)
        self.char_count_var.set(f"{char_count}/{self.remaining_chars}")
        if remaining < 100:
            self.char_count_label.config(foreground="red")

    def load_regions(self):
        """Load available AWS regions that support Polly"""
        try:
            supported_regions = self.polly_manager.get_supported_regions()
            
            if not supported_regions:
                self.update_status("No AWS regions with Polly support found", is_error=True)
                return
            
            self.main_ui.region_dropdown['values'] = supported_regions
            if supported_regions:
                self.region_var.set('us-east-1' if 'us-east-1' in supported_regions else supported_regions[0])
                self.update_engines_for_region()
                
            self.update_status(f"Loaded {len(supported_regions)} available regions")
            
        except Exception as e:
            self.update_status(f"Error loading regions: {str(e)}", is_error=True)

    def update_engines_for_region(self, event=None):
        """Update available engines based on selected region"""
        try:
            selected_region = self.region_var.get()
            if not selected_region:
                return
                
            available_engines = self.polly_manager.get_engines_for_region(selected_region)
            self.main_ui.engine_dropdown['values'] = available_engines
            
            if available_engines:
                preferred_order = ['neural', 'generative', 'long-form', 'standard']
                for engine in preferred_order:
                    if engine in available_engines:
                        self.engine_var.set(engine)
                        self.update_output_formats()
                        break
            else:
                self.update_status(f"No engines available in {selected_region}", is_error=True)
                
        except Exception as e:
            self.update_status(f"Error updating engines: {str(e)}", is_error=True)

    def update_languages(self, event=None):
        """Update available languages"""
        region = self.region_var.get()
        engine = self.engine_var.get()
        
        success, error_msg = self.polly_manager.get_languages(region, engine)
        
        if not success:
            self.update_status(
                "Failed to load languages, please select a different region", 
                is_error=True
            )
            print(f"Error loading languages: {error_msg}")
            self.main_ui.language_dropdown['values'] = []
            self.language_var.set("")
            self.main_ui.voice_dropdown['values'] = []
            self.voice_var.set("")
            return
            
        try:            
            languages = sorted(
                [(code, name) for code, name in self.polly_manager.language_map.items()],
                key=lambda x: x[1]
            )
            
            # Create display strings
            language_displays = [f"{name} ({code})" for code, name in languages]
            self.main_ui.language_dropdown['values'] = language_displays
            
            if languages:
                # Find US English by code
                us_english = next(
                    (f"{name} ({code})" for code, name in languages if code == 'en-US'),
                    None
                )
                
                # Set to US English if available, otherwise first language
                default_lang = us_english if us_english else f"{languages[0][1]} ({languages[0][0]})"
                self.language_var.set(default_lang)
                self.update_voices()
                
            self.update_status(f"Loaded {len(languages)} languages")
            
        except Exception as e:
            self.update_status(f"Error updating languages: {str(e)}", is_error=True)

    def update_voices(self, event=None):
        """Update available voices with gender filtering"""
        try:
            selected_lang = self.language_var.get()
            if not selected_lang:
                return
                
            lang_code = selected_lang.split('(')[-1].rstrip(')')
            selected_gender = self.gender_var.get()
            
            voices = self.polly_manager.get_voices(
                lang_code, 
                self.engine_var.get(), 
                self.region_var.get(),
                selected_gender
            )
            
            self.main_ui.voice_dropdown['values'] = voices
            if voices:
                self.voice_var.set(voices[0])
            else:
                self.voice_var.set("")
                
            gender_text = f" ({selected_gender})" if selected_gender != "All" else ""
            self.update_status(f"Loaded {len(voices)} {self.engine_var.get()} voices for {selected_lang}{gender_text}")
            
        except Exception as e:
            self.update_status(f"Error updating voices: {str(e)}", is_error=True)

    def update_gender_filter(self, event=None):
        """Update voices when gender filter changes"""
        self.update_voices()

    def get_available_genders_for_language(self, language):
        """Get available genders for a specific language"""
        try:
            lang_code = language.split('(')[-1].rstrip(')')
            return self.polly_manager.get_available_genders_for_language(
                lang_code, 
                self.engine_var.get(), 
                self.region_var.get()
            )
        except Exception as e:
            print(f"Error getting genders for language: {e}")
            return ["All", "Male", "Female"]

    def update_output_formats(self, event=None):
        """Update available output formats and sample rates"""
        try:
            self.main_ui.format_dropdown['values'] = self.polly_manager.OUTPUT_FORMATS
            if self.polly_manager.OUTPUT_FORMATS:
                self.output_format_var.set('mp3')
                self.update_sample_rates()
            
            self.update_languages()
        except Exception as e:
            self.update_status(f"Error updating formats: {str(e)}", is_error=True)

    def update_sample_rates(self, event=None):
        """Update available sample rates based on output format and engine"""
        try:
            output_format = self.output_format_var.get()
            engine = self.engine_var.get()
            
            rates = self.polly_manager.get_sample_rates(output_format)
            self.main_ui.sample_rate_dropdown['values'] = rates
            
            # Set default sample rate
            if output_format == 'pcm':
                self.sample_rate_var.set("16000")
            elif engine == 'standard':
                self.sample_rate_var.set("22050")
            else:  # neural/long-form/generative
                self.sample_rate_var.set("24000")
                    
        except Exception as e:
            self.update_status(f"Error updating sample rates: {str(e)}", is_error=True)

    def verify_and_continue(self):
        """Verify credentials and continue to main polly interface"""
        self.status_bar.update_status("Verifying AWS credentials...")
        self.main_frame.master.update()
        
        try:
            access_key = self.access_key_var.get().strip()
            secret_key = self.secret_key_var.get().strip()
            
            if not access_key or not secret_key:
                self.status_bar.update_status("Both Access Key and Secret Key are required", is_error=True)
                self.main_frame.master.update()
                messagebox.showerror("Error", "Both Access Key and Secret Key are required")
                return

            session = self.polly_manager.get_session()

            # Test the credentials by making a simple AWS call
            self.status_bar.update_status("Authenticating with AWS...")
            self.main_frame.master.update()
            
            sts = session.client('sts')
            sts.get_caller_identity()
            
            # Only save if credentials are valid
            if self.remember_var.get():
                self.status_bar.update_status("Saving credentials...")
                self.main_frame.master.update()
                
                if not self.credentials_manager.save_credentials(True):
                    self.status_bar.update_status("Warning: Could not save credentials to keyring", is_error=True)
                    self.main_frame.master.update()
                    messagebox.showwarning("Warning", "Could not save credentials to keyring")
                else:
                    self.status_bar.update_status("Credentials saved securely")
                    self.main_frame.master.update()
            
            self.status_bar.update_status("Credentials verified successfully!")
            self.main_frame.master.update()
            self._show_polly_main_interface()
            
        except Exception as e:
            error_msg = self._parse_aws_error(e)
            self.status_bar.update_status(f"Verification failed: {error_msg}", is_error=True)
            self.main_frame.master.update()
            messagebox.showerror("AWS Error", f"Invalid credentials: {error_msg}")

    def _parse_aws_error(self, error):
        """Parse AWS error messages to be more user-friendly"""
        error_msg = str(error)
        
        # Connection related errors
        if "EndpointConnectionError" in error_msg:
            return "Could not connect to AWS - check your internet connection"
        elif "ConnectionError" in error_msg:
            return "Network connection error - please check your internet"
        
        # Credential specific errors
        elif "InvalidClientTokenId" in error_msg:
            return "The AWS Access Key ID is invalid"
        elif "SignatureDoesNotMatch" in error_msg:
            return "The AWS Secret Access Key is invalid"
        elif "AuthFailure" in error_msg:
            return "Authentication failed - check your credentials"
        elif "ExpiredToken" in error_msg:
            return "Credentials have expired - please generate new ones"
        
        # General AWS errors
        elif "AccessDenied" in error_msg:
            return "Access denied - the credentials don't have proper permissions"
        
        return f"AWS Error: {error_msg.split(':')[-1].strip()}"

    def _validate_synthesis_inputs(self):
        """Validate inputs for synthesis"""
        if not hasattr(self, 'main_ui'):
            self.update_status("UI not initialized.", is_error=True)
            return None
            
        text = self.main_ui.text_input.get("1.0", tk.END).strip()
        
        if not text:
            self.update_status("Please enter text.", is_error=True)
            return None
        
        if not all([self.access_key_var.get(), self.secret_key_var.get(), self.region_var.get()]):
            self.update_status("AWS configuration is incomplete.", is_error=True)
            return None
            
        if not self.voice_var.get():
            self.update_status("Please select a voice.", is_error=True)
            return None
        
        return text

    def generate(self):
        """Generate speech from text"""
        text = self._validate_synthesis_inputs()
        if not text:
            return
        
        try:
            voice_id = self.polly_manager.get_voice_id_from_display(self.voice_var.get())
            engine = self.engine_var.get()
            output_format = self.output_format_var.get()
            
            self.status_bar.update_status("Generating...")
            self.main_frame.master.update()

            response = self.polly_manager.synthesize_speech(
                region=self.region_var.get(),
                text=text,
                voice_id=voice_id,
                engine=engine,
                output_format=output_format,
                sample_rate=self.sample_rate_var.get()
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                
            format_to_extension = {
                'mp3': 'mp3',
                'ogg_vorbis': 'ogg',
                'pcm': 'pcm'
            }
            
            ext = format_to_extension.get(output_format, 'mp3')
            output_path = os.path.join(output_dir, f"tts_output_{voice_id}_{timestamp}.{ext}")
            
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
                
            self.update_status(f"Audio saved to: {output_path}")
            
            # Open file explorer to show the file
            self._open_file_location(output_path)
                
        except Exception as e:
            self.update_status(f"Error: {str(e)}", is_error=True)

    def play_audio_directly(self):
        """Generate and play audio without saving"""
        text = self._validate_synthesis_inputs()
        if not text:
            return
        
        try:
            self.status_bar.update_status("Generating...")
            self.main_frame.master.update()

            voice_id = self.polly_manager.get_voice_id_from_display(self.voice_var.get())
            output_format = self.output_format_var.get()
            
            response = self.polly_manager.synthesize_speech(
                region=self.region_var.get(),
                text=text,
                voice_id=voice_id,
                engine=self.engine_var.get(),
                output_format=output_format,
                sample_rate=self.sample_rate_var.get()
            )

            # Create temp file with appropriate extension
            if output_format == 'mp3':
                suffix = '.mp3'
            elif output_format == 'ogg_vorbis':
                suffix = '.ogg'
            else:
                suffix = '.wav'

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                audio_data = response['AudioStream'].read()
                
                if output_format == 'pcm':
                    # Convert PCM to WAV for playback
                    import struct
                    sample_rate = int(self.sample_rate_var.get())
                    # Write simple WAV header for PCM
                    tmp_file.write(b'RIFF')
                    tmp_file.write(struct.pack('<I', 36 + len(audio_data)))
                    tmp_file.write(b'WAVE')
                    tmp_file.write(b'fmt ')
                    tmp_file.write(struct.pack('<I', 16))
                    tmp_file.write(struct.pack('<H', 1))
                    tmp_file.write(struct.pack('<H', 1))
                    tmp_file.write(struct.pack('<I', sample_rate))
                    tmp_file.write(struct.pack('<I', sample_rate * 2))
                    tmp_file.write(struct.pack('<H', 2))
                    tmp_file.write(struct.pack('<H', 16))
                    tmp_file.write(b'data')
                    tmp_file.write(struct.pack('<I', len(audio_data)))
                    tmp_file.write(audio_data)
                else:
                    tmp_file.write(audio_data)
                
                tmp_file.flush()
                temp_path = tmp_file.name
                
            self._play_audio_file(temp_path)
            self.update_status("Audio played successfully")
            
        except Exception as e:
            self.update_status(f"Playback error: {str(e)}", is_error=True)

    def on_language_changed(self, event=None):
        """Handle language change event"""
        selected_lang = self.language_var.get()
        if selected_lang and hasattr(self, 'main_ui'):
            # Update available genders for the selected language
            available_genders = self.get_available_genders_for_language(selected_lang)
            self.main_ui.gender_dropdown['values'] = available_genders
            self.gender_var.set("All")
        
        # Update voices for the new language
        self.update_voices()

    def _open_file_location(self, file_path):
        """Open file location in system file manager"""
        if platform.system() == "Darwin":
            subprocess.run(["open", "-R", file_path])
        elif platform.system() == "Windows":
            subprocess.run(["explorer", "/select,", file_path])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", os.path.dirname(file_path)])

    def _play_audio_file(self, file_path):
        """Play audio file using system player"""
        try:
            if platform.system() == "Darwin":
                subprocess.run(["afplay", file_path])
            elif platform.system() == "Windows":
                subprocess.run(["start", file_path], shell=True)
            elif platform.system() == "Linux":
                subprocess.run(["aplay", file_path])
        finally:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def update_status(self, message, is_error=False):
        """Update status bar with message"""
        self.status_bar.update_status(message, is_error)

    @property
    def text_input(self):
        return self.main_ui.text_input

    @property
    def char_count_label(self):
        return self.main_ui.char_count_label
