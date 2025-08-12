import boto3

class AWSPollyManager:
    """Manages AWS Polly operations and configurations"""
    ENGINE_REGIONS = {
        'standard': [
            'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'af-south-1', 
            'ap-east-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3', 'ap-south-1', 
            'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-5', 'cn-northwest-1', 'ca-central-1', 
            'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 'eu-south-2',
            'eu-north-1', 'me-south-1', 'sa-east-1', 'us-gov-west-1'
        ],
        'neural': [
            'us-east-1', 'us-west-2', 'af-south-1', 'ap-northeast-1', 'ap-northeast-2',
            'ap-northeast-3', 'ap-south-1', 'ap-southeast-1', 'ap-southeast-2', 'ap-southeast-5',
            'ca-central-1', 'eu-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3', 
            'eu-south-2', 'us-gov-west-1'
        ],
        'long-form': ['us-east-1'],
        'generative': ['us-east-1', 'us-west-2', 'eu-central-1']
    }
    
    OUTPUT_FORMATS = ['mp3', 'ogg_vorbis', 'pcm']
    
    SAMPLE_RATES = {
        'mp3': ["8000", "16000", "22050", "24000"],
        'ogg_vorbis': ["8000", "16000", "22050", "24000"], 
        'pcm': ["8000", "16000"]
    }

    def __init__(self, access_key_var, secret_key_var):
        self.access_key_var = access_key_var
        self.secret_key_var = secret_key_var
        self.language_map = {}
        self.voices_data = {}

    def _get_client(self, region):
        """Get Polly client"""
        return boto3.client(
            'polly',
            aws_access_key_id=self.access_key_var.get(),
            aws_secret_access_key=self.secret_key_var.get(),
            region_name=region
        )
    
    def get_session(self):
        """Get a boto3 session with the provided credentials"""
        return boto3.Session(
            aws_access_key_id=self.access_key_var.get(),
            aws_secret_access_key=self.secret_key_var.get()
        )

    def get_supported_regions(self):
        """Get all regions supporting Polly"""
        session = self.get_session()
        regions = session.get_available_regions('polly')
        return sorted(regions) if regions else []

    def get_engines_for_region(self, region):
        """Get available engines for a region"""
        return [engine for engine, regions in self.ENGINE_REGIONS.items() 
                if region in regions]

    def get_sample_rates(self, output_format):
        """Get sample rates for format/engine combo"""
        return self.SAMPLE_RATES.get(output_format, [])

    def get_languages(self, region, engine):
        """Get available languages and store voice data"""
        try:
            client = self._get_client(region)
            response = client.describe_voices(Engine=engine)
            
            # Store both language map and voices data
            self.language_map = {
                v['LanguageCode']: v['LanguageName'] 
                for v in response['Voices']
            }
            
            # Store voices data grouped by language code
            self.voices_data = {}
            for voice in response['Voices']:
                lang_code = voice['LanguageCode']
                if lang_code not in self.voices_data:
                    self.voices_data[lang_code] = []
                self.voices_data[lang_code].append(voice)
            
            return (True, None)
        except Exception as e:
            error_msg = str(e)
            return (False, error_msg)

    def get_voices(self, language_code, engine, region, gender_filter="All"):
        """Get voices for specific language with optional gender filter"""
        try:
            client = self._get_client(region)
            response = client.describe_voices(
                Engine=engine,
                LanguageCode=language_code
            )
            
            voices = response['Voices']
            
            # Filter by gender if not "All"
            if gender_filter != "All":
                voices = [v for v in voices if v['Gender'] == gender_filter]
            
            return [f"{v['Id']} ({v['Gender']})" for v in voices]
        except Exception as e:
            print(f"Error getting voices: {str(e)}")
            return []

    def get_available_genders_for_language(self, language_code, engine, region):
        """Get available genders for a specific language"""
        try:
            client = self._get_client(region)
            response = client.describe_voices(
                Engine=engine,
                LanguageCode=language_code
            )
            
            genders = set()
            for voice in response['Voices']:
                genders.add(voice['Gender'])
            
            return ["All"] + sorted(list(genders))
        except Exception as e:
            print(f"Error getting genders for language: {e}")
            return ["All", "Male", "Female"]

    def get_voice_id_from_display(self, voice_display):
        """Extract voice ID from display string (e.g., 'Joanna (Female)' -> 'Joanna')"""
        return voice_display.split(' ')[0] if voice_display else ""

    def synthesize_speech(self, region, text, voice_id, engine, output_format, sample_rate):
        """Generate speech synthesis"""
        client = self._get_client(region)
        return client.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            Engine=engine,
            OutputFormat=output_format,
            SampleRate=sample_rate
        )