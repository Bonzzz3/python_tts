import boto3
from dotenv import load_dotenv
import os
import re
from datetime import datetime

load_dotenv()

polly = boto3.client('polly',
                    region_name=os.getenv('AWS_REGION'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

output_dir = "polly_output/samples_output"
os.makedirs(output_dir, exist_ok=True)

# Voice configurations
VOICES = {
    "Standard": {"VoiceId": "Joanna", "Engine": "standard"},
    "Neural": {"VoiceId": "Danielle", "Engine": "neural"},
    "Long-Form": {"VoiceId": "Danielle", "Engine": "long-form"},
    "Generative": {"VoiceId": "Danielle", "Engine": "generative"}
}

def clean_ssml(ssml_text):
    clean_text = re.sub('<[^>]+>', '', ssml_text)
    return ' '.join(clean_text.split())

def generate_audio_samples():

    concept_text = """Let's discuss the SOLID principles of software design. 
    These are five key principles that help us create better, more maintainable software.

    First, S - the Single Responsibility Principle (SRP).
    Next, O - the Open-Closed Principle (OCP). 
    Then we have L - the Liskov Substitution Principle (LSP). 
    Moving to I - the Interface Segregation Principle (ISP). 
    Finally, D - the Dependency Inversion Principle (DIP).

    Together, these SOLID principles help us design systems 
    that are more robust, maintainable, and adaptable to change.
    The script is adapted from the CS2103 online textbook."""

    results = []
    
    for voice_name, config in VOICES.items():
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = f"{output_dir}/se_concept_{voice_name.lower()}_{timestamp}.mp3"
            text_file = f"{output_dir}/se_script_{voice_name.lower()}_{timestamp}.txt"
            
            print(f"Generating {voice_name} voice...")
            
            response = polly.synthesize_speech(
                Text=concept_text,
                TextType='text',
                VoiceId=config["VoiceId"],
                Engine=config["Engine"],
                OutputFormat='mp3'
            )
            
            with open(audio_file, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            with open(text_file, 'w') as f:
                f.write(clean_ssml(concept_text))
            
            print(f"  Audio generated: {audio_file}")
            print(f"  Transcript saved: {text_file}\n")
            
            results.append({
                "voice_type": voice_name,
                "audio_file": audio_file,
                "text_file": text_file
            })
            
        except Exception as e:
            print(f"Generation failed for {voice_name}: {str(e)}")
            results.append({
                "voice_type": voice_name,
                "error": str(e)
            })
    
    return results

if __name__ == "__main__":
    print("Generating audio samples for all voice types...\n")
    samples = generate_audio_samples()
    
    print("\nGeneration complete. Summary:")
    for sample in samples:
        if "error" in sample:
            print(f"{sample['voice_type']}: Failed - {sample['error']}")
        else:
            print(f"{sample['voice_type']}: Success")