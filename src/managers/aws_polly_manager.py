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

    def _get_client(self, region):
        """Get Polly client"""
        return boto3.client(
            'polly',
            aws_access_key_id=self.access_key_var.get(),
            aws_secret_access_key=self.secret_key_var.get(),
            region_name=region
        )

    def get_supported_regions(self):
        """Get all regions supporting Polly"""
        session = boto3.Session(
            aws_access_key_id=self.access_key_var.get(),
            aws_secret_access_key=self.secret_key_var.get(),
        )
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
        """Get available languages"""
        try:
            client = self._get_client(region)
            response = client.describe_voices(Engine=engine)
            
            self.language_map = {
                v['LanguageCode']: v['LanguageName'] 
                for v in response['Voices']
            }
            return (True, None)
        except Exception as e:
            error_msg = str(e)
            return (False, error_msg)

    def get_voices(self, language_code, engine, region):
        """Get voices for specific language"""
        try:
            client = self._get_client(region)
            response = client.describe_voices(
                Engine=engine,
                LanguageCode=language_code
            )
            return [f"{v['Id']} ({v['Gender']})" for v in response['Voices']]
        except Exception as e:
            print(f"Error getting voices: {str(e)}")
            return []

    def synthesize_speech(self, region, text, voice_id, engine,output_format, sample_rate):
        """Generate speech synthesis"""
        client = self._get_client(region)
        return client.synthesize_speech(
            Text=text,
            VoiceId=voice_id,
            Engine=engine,
            OutputFormat=output_format,
            SampleRate=sample_rate
        )