from datetime import datetime
import boto3
from dotenv import load_dotenv
import os
import time

load_dotenv()

polly = boto3.client('polly',
                    region_name=os.getenv('AWS_REGION'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

output_dir = "polly_output/analysis_output"
os.makedirs(output_dir, exist_ok=True)

# Complex test text with numbers, difficult words, and edge cases
TEST_TEXT = """
1. Scientific Terms: 
   - Photosynthesis
   - Chlorella vulgaris
   - Schrödinger's cat
   - 2H₂ + O₂ -> 2H₂O (exothermic, -285.8 kJ/mol).

2. Programming & Names:
   - @Override annotation in Java. 
   - Git commands: `git rebase --onto` vs `git merge --no-ff`.
   - Dr. Agnieszka Łukasik (Polish name) and François Hollande (French).

3. Numbers & Formats:
   - $1,234.56 USD or €789,00.
   - 5⅛ inches ≈ 13.0175 cm.
   - 0xDEADBEEF (hex) vs 3.14159 (pi).
   - 2025-12-31 (ISO date) vs 12/31/25 (US format).

4. Ambiguous Words:
   - "Bass". I caught a bass. I play bass guitar.
   - "Tear". I shed a tear. I will tear the paper.
   - "Bow". I will bow to the king. I shot an arrow with my bow.
   - "Lead". The guide will lead us. The pipe is made of lead.
   - "Wind". The wind is strong. I will wind the clock.

5. Complex Sentence:
   - The 120dB noise from the F-22 Raptor's Pratt & Whitney F119 engine exceeded OSHA's PEL of 90dB.
"""

# Voice configurations
VOICES = {
    "Standard": {"VoiceId": "Joanna", "Engine": "standard"},
    "Neural": {"VoiceId": "Danielle", "Engine": "neural"},
    "Long-Form": {"VoiceId": "Danielle", "Engine": "long-form"},
    "Generative": {"VoiceId": "Danielle", "Engine": "generative"}
}

def generate_audio(text, voice_config):
    start_time = time.time()
    
    try:
        response = polly.synthesize_speech(
            Text=text,
            TextType='text',
            VoiceId=voice_config["VoiceId"],
            Engine=voice_config["Engine"],
            OutputFormat='mp3',
            SampleRate='24000'
        )
        
        generation_time = time.time() - start_time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        engine_name = voice_config["Engine"]
        audio_file = f"{output_dir}/{engine_name}_{timestamp}.mp3"
        
        with open(audio_file, 'wb') as f:
            f.write(response['AudioStream'].read())
        
        print(f"Generated {engine_name.ljust(10)} in {generation_time:.2f}s | {audio_file}")
        return audio_file, generation_time
        
    except Exception as e:
        print(f"Error with {voice_config['Engine']}: {str(e)}")
        return None, None

if __name__ == "__main__":
    print("=== Testing Pronunciation Complexity ===")
    print(f"Text length: {len(TEST_TEXT.split())} words\n")
    
    results = []
    for voice_name, config in VOICES.items():
        audio_file, time_taken = generate_audio(TEST_TEXT, config)
        if audio_file:
            results.append((voice_name, time_taken))
    
    # Summary
    print("\n=== Results ===")
    print(f"{'Engine'.ljust(12)} | Time (s)")
    print("-" * 30)
    for voice, speed in sorted(results, key=lambda x: x[1]):
        # Manual scoring guide (adjust after listening)
        pronunciation_score = {
            "Standard": 2,
            "Neural": 3,
            "Long-Form": 4,
            "Generative": 5
        }.get(voice, 0)
        print(f"{voice.ljust(12)} | {speed:.2f}")