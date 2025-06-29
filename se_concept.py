import boto3
from dotenv import load_dotenv
import os
import re

load_dotenv()

polly = boto3.client('polly',
                    region_name=os.getenv('AWS_REGION'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

output_dir = "polly_output"
os.makedirs(output_dir, exist_ok=True)

def clean_ssml(ssml_text):
    clean_text = re.sub('<[^>]+>', '', ssml_text)
    return ' '.join(clean_text.split())

def generate_se_concept_audio():
    concept_text = """
    <speak>
    Let's discuss the SOLID principles of software design. 
    These are five key principles that help us create better, more maintainable software.
    <break time="700ms"/>

    First, S - the Single Responsibility Principle (SRP). 
    This means a class should have only one responsibility, 
    so it only needs to change when that one responsibility changes. 
    <break time="500ms"/>
    For example, if we have a TextUi class 
    that handles both parsing user commands and interacting with the user, 
    this violates SRP. 
    <break time="400ms"/>
    Why? Because now this class needs to change 
    whenever we modify the UI formatting 
    <break time="200ms"/>
    and whenever we change the command syntax.
    <break time="800ms"/>

    Next, O - the Open-Closed Principle (OCP). 
    This principle states that software entities should be 
    open for extension but closed for modification. 
    <break time="500ms"/>
    In object-oriented programming, we achieve this by separating 
    a module's interface from its implementation. 
    <break time="400ms"/>
    This way we can extend behavior without modifying existing code.
    <break time="800ms"/>

    Then we have L - the Liskov Substitution Principle (LSP). 
    <break time="400ms"/>
    While this sounds similar to basic substitutability, 
    LSP goes further. 
    It specifies that a subclass shouldn't be more restrictive than its superclass. 
    <break time="500ms"/>
    Even though Java supports substitutability at the language level, 
    violating LSP can still break your code 
    when substituting subclass objects for superclass objects.
    <break time="800ms"/>

    Moving to I - the Interface Segregation Principle (ISP). 
    <break time="400ms"/>
    This principle clearly states: 
    no client should be forced to depend on methods it doesn't use. 
    <break time="500ms"/>
    Instead of large general-purpose interfaces, 
    we should create smaller, more specific ones.
    <break time="800ms"/>

    Finally, D - the Dependency Inversion Principle (DIP). 
    <break time="400ms"/>
    This has two key parts:
    <break time="500ms"/>
    <say-as interpret-as="characters">1</say-as>. High-level modules shouldn't depend on low-level modules - 
    both should depend on abstractions
    <break time="600ms"/>
    <say-as interpret-as="characters">2</say-as>. Abstractions shouldn't depend on details - 
    details should depend on abstractions
    <break time="800ms"/>

    <break time="1s"/>
    Together, these <say-as interpret-as="characters">SOLID</say-as> principles help us design systems 
    that are more robust, maintainable, 
    and adaptable to change.
    <break time="500ms"/>
    The script is adapted from the <say-as interpret-as="characters">CS2103</say-as> online textbook.
    </speak>
    """

    try:
        response = polly.synthesize_speech(
            Text=concept_text,
            TextType='ssml',
            VoiceId='Joanna',
            Engine='neural',
            OutputFormat='mp3'
        )

        audio_file = f"{output_dir}/se_concept.mp3"
        text_file = f"{output_dir}/se_script.txt"
        
        with open(audio_file, 'wb') as f:
            f.write(response['AudioStream'].read())
        
        with open(text_file, 'w') as f:
            f.write(clean_ssml(concept_text))
        
        print(f"Audio generated: {audio_file}")
        print(f"Transcript saved: {text_file}")
        
        return audio_file, text_file
        
    except Exception as e:
        print(f"Generation failed: {str(e)}")
        return None, None

if __name__ == "__main__":
    audio, transcript = generate_se_concept_audio()