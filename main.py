import os
import boto3
from dotenv import load_dotenv

load_dotenv()

polly = boto3.client('polly',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION'))

try:
    response = polly.synthesize_speech(
        Engine='neural',
        LanguageCode='en-US',
        Text='Hi! This is a test input text for a python TTS app.',
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)

with open('output.mp3', 'wb') as f:
    f.write(response['AudioStream'].read())

print("Audio saved.")