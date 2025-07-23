import os
import tempfile
from datetime import datetime
import azure.cognitiveservices.speech as speechsdk
from babel import Locale as BabelLocale
from babel.core import UnknownLocaleError

class AzureSpeechManager:
    """Manages Azure Speech Services TTS operations"""
    
    def __init__(self):
        self.available_voices = []
        self.language_voice_map = {}
        self.voices_loaded = False
    
    def test_credentials(self, api_key, endpoint):
        """Test Azure credentials by attempting a simple synthesis"""
        try:
            # Test the credentials by creating a speech config
            speech_config = speechsdk.SpeechConfig(subscription=api_key, endpoint=endpoint)
            speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
            
            # Simple test synthesis to verify credentials
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = synthesizer.speak_text_async("test").get()
            
            return result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted
        except Exception as e:
            raise Exception(f"Credential verification failed: {str(e)}")
    
    def fetch_available_voices(self, api_key, endpoint):
        """Fetch available voices using Azure Speech SDK"""
        try:
            # Create speech config
            speech_config = speechsdk.SpeechConfig(
                subscription=api_key,
                endpoint=endpoint
            )
            
            # Create synthesizer to get voice list
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            
            # Get voices using the synthesizer
            voices_result = synthesizer.get_voices_async().get()
            
            if voices_result.reason == speechsdk.ResultReason.VoicesListRetrieved:
                self._process_voices_from_sdk(voices_result.voices)
                self.voices_loaded = True
                return True, f"Successfully loaded {len(self.available_voices)} voices"
            else:
                error_msg = f"Failed to fetch voices: {voices_result.reason}"
                if hasattr(voices_result, 'error_details') and voices_result.error_details:
                    error_msg += f" - {voices_result.error_details}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error fetching voices: {str(e)}"
    
    def _process_voices_from_sdk(self, voices_list):
        """Process the voices data from Azure SDK and organize by language"""
        self.available_voices = voices_list
        self.language_voice_map = {}
        
        # Group voices by locale
        for voice in voices_list:
            locale = voice.locale
            display_name = voice.local_name
            short_name = voice.short_name
            
            if not locale or not short_name:
                continue
            
            # Get language name
            lang_name = self._get_dynamic_language_name(voice, locale)
            
            if lang_name not in self.language_voice_map:
                self.language_voice_map[lang_name] = {
                    "code": locale,
                    "voices": []
                }
            
            # Add voice with display name and gender info if available
            gender = voice.gender.name if hasattr(voice.gender, 'name') else str(voice.gender)
            voice_display = f"{short_name}"
            if display_name and display_name != short_name:
                voice_display += f" ({display_name})"
            if gender and gender != 'Unknown':
                voice_display += f" - {gender}"
            
            self.language_voice_map[lang_name]["voices"].append({
                "display": voice_display,
                "short_name": short_name,
                "locale": locale
            })
        
        # Sort languages and voices
        for lang_data in self.language_voice_map.values():
            lang_data["voices"].sort(key=lambda x: x["display"])
    
    def _get_dynamic_language_name(self, voice, locale):
        """Get language name dynamically from voice data or use babel library"""
        # Ensure we never return None
        if not locale:
            return "Unknown"
            
        try:
            # Convert locale format (en-US to en_US)
            babel_locale = locale.replace('-', '_')
            loc = BabelLocale.parse(babel_locale)
            display_name = loc.display_name
            # Ensure display_name is not None
            return display_name if display_name else locale
        except (UnknownLocaleError, ValueError):
            pass
        
        return str(locale) if locale else "Unknown"
    
    def get_languages(self):
        """Get list of available languages"""
        if not self.voices_loaded:
            return []
        
        # Filter out any None keys and ensure all are strings
        language_keys = [key for key in self.language_voice_map.keys() if key is not None]
        return sorted(language_keys)
    
    def get_voices_for_language(self, language):
        """Get voices for a specific language"""
        if language not in self.language_voice_map:
            return []
        
        voices_data = self.language_voice_map[language]["voices"]
        return [voice["display"] for voice in voices_data]
    
    def get_voice_short_name(self, voice_display, language):
        """Get the actual voice short name from the display name"""
        if language not in self.language_voice_map:
            return voice_display
        
        voices_data = self.language_voice_map[language]["voices"]
        for voice in voices_data:
            if voice["display"] == voice_display:
                return voice["short_name"]
        
        return voice_display
    
    def synthesize_to_file(self, text, api_key, endpoint, voice_short_name, output_path):
        """Synthesize speech and save to file"""
        try:
            # Configure speech synthesis
            speech_config = speechsdk.SpeechConfig(
                subscription=api_key, 
                endpoint=endpoint
            )
            speech_config.speech_synthesis_voice_name = voice_short_name
            
            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=output_path)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True, f"Audio saved to: {output_path}"
            else:
                cancellation_details = result.cancellation_details
                error_msg = f"Speech synthesis failed: {cancellation_details.reason}"
                if cancellation_details.error_details:
                    error_msg += f" - {cancellation_details.error_details}"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def synthesize_to_temp_file(self, text, api_key, endpoint, voice_short_name):
        """Synthesize speech to a temporary file and return the path"""
        try:
            # Configure speech synthesis
            speech_config = speechsdk.SpeechConfig(
                subscription=api_key, 
                endpoint=endpoint
            )
            speech_config.speech_synthesis_voice_name = voice_short_name
            
            # Create temp file for playback
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Configure audio output to temp file
            audio_config = speechsdk.audio.AudioOutputConfig(filename=tmp_path)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
            
            # Synthesize speech
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return True, tmp_path, "Audio synthesized successfully"
            else:
                cancellation_details = result.cancellation_details
                error_msg = f"Speech synthesis failed: {cancellation_details.reason}"
                if cancellation_details.error_details:
                    error_msg += f" - {cancellation_details.error_details}"
                return False, None, error_msg
                
        except Exception as e:
            return False, None, f"Synthesis error: {str(e)}"
    
    def generate_output_filename(self, voice_short_name, output_dir=None):
        """Generate a timestamped output filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_dir is None:
            output_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        voice_name = voice_short_name.replace("-", "_")
        return os.path.join(output_dir, f"azure_tts_{voice_name}_{timestamp}.wav")
