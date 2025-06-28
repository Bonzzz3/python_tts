import boto3
import os
from dotenv import load_dotenv

load_dotenv()

polly = boto3.client('polly',
                    region_name=os.getenv('AWS_REGION'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

os.makedirs('polly_output', exist_ok=True)

# Basic tts conversion
def basic_tts():
    text = "This is a basic test of Amazon Polly text-to-speech service."
    
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna'
    )
    
    with open('polly_output/basic.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print("Basic TTS audio saved as polly_output/basic.mp3")

# SSML
def ssml_experiment():
    # @@author benchilds
    # Reused from "https://gist.github.com/benchilds/9baee11ada8c6ea251681e39424a1fa9"
    ssml_text = """
    <speak>
    <amazon:auto-breaths>

        <!-- Auto-breaths using the <amazon:auto-breaths> tag and sentences structured using the <p> tag -->
        <p>With auto-breaths enabled and sentences structured as paragraphs, most text is handled well by Amazon Polly.</p>

        <!-- Manual breaths using the <amazon:breath> tag and pauses using the <break> tag -->
        <p>Of course, <amazon:breath duration="x-long" volume="x-loud"/> you can still add manual breaths <amazon:breath duration="x-long" volume="x-loud"/> if you need them. Or a short pause<break time="1000ms"/> can be added using the break tag.</p>

        <!-- Adding stress using the <emphasis> tag -->
        <p>If you need to <emphasis level="strong">really emphasize something</emphasis> you can do this with the emphasis tag.</p>

        <!-- Rate, pitch and volume using the <prosody> tag (present and value attributes) -->
        <p>However, <prosody rate="+5%" pitch="-10%">as described in the article</prosody>, using the <prosody volume="+15dB">emphasis tag</prosody> with the strong attribute <prosody rate="+10%">often sounds slightly clumsy</prosody>, so, in practice, controlling the pitch, rate and volume with <prosody rate="+5%">the prosody tag</prosody> works better. Wouldn't you <prosody pitch="+5%">agree?</prosody></p>

        <!-- Adding context assistance using the <say-as> tag -->
        <p>If <say-as interpret-as="spell-out">TUT</say-as> Software launch their new API as planned on <say-as interpret-as="date" format="dm">17/06</say-as>, it will be only <say-as interpret-as="fraction">0.5</say-as> the expected price to use. That's absolutely <say-as interpret-as="expletive">bloody</say-as> amazing.</p>

        <!-- Adding context for coded words using the <sub> tag -->
        <p>When I was last in <sub alias="Australia">au</sub> I went searching for <sub alias="gold">au</sub>.</p>

        <!-- Pronouncing sounds explicitly using the <phoneme> tag -->
        <p>Mary Poppins sang the song dorayme. I mean, do ray me. Hang on. I mean, <amazon:breath duration="x-long" volume="x-loud"/> <phoneme alphabet="ipa" ph="dəʊ">Do</phoneme>.<phoneme alphabet="ipa" ph="ɹeɪˈ">Ray</phoneme>.<phoneme alphabet="ipa" ph="mi:">Me</phoneme>.</p>

    </amazon:auto-breaths>
    </speak>
    """
    # @@author benchilds
    
    response = polly.synthesize_speech(
        Text=ssml_text,
        TextType='ssml',
        OutputFormat='mp3',
        VoiceId='Matthew'
    )
    
    with open('polly_output/ssml.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print("SSML audio saved as polly_output/ssml.mp3")

# Neural Voices
def neural_voice_experiment():
    text = "Amazon Polly has a Neural text-to-speech (NTTS) engine that can produce even higher quality voices than its standard voices."
    
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Joanna',
        Engine='neural'
    )
    
    with open('polly_output/neural.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print("Neural voice audio saved as polly_output/neural.mp3")

# Lexicon
def lexicon_experiment():
    """Step 5: Use custom pronunciation dictionary"""
    lexicon = """<?xml version="1.0" encoding="UTF-8"?>
    <lexicon version="1.0"
        xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon
            http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"
        alphabet="ipa"
        xml:lang="en-US">
        <lexeme>
            <grapheme>API</grapheme>
            <alias>Application programming interface</alias>
        </lexeme>
    </lexicon>"""
    
    polly.put_lexicon(Name='lexicon', Content=lexicon)
    
    response = polly.synthesize_speech(
        Text="We use an API to connect systems.",
        OutputFormat='mp3',
        VoiceId='Joanna',
        LexiconNames=['lexicon']
    )
    
    with open('polly_output/lexicon.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())
    print("Lexicon-based audio saved as polly_output/lexicon.mp3")

# Speech Marks
def speech_marks_experiment():
    text = "Speech marks are metadata that describe the speech that you synthesize, such as where a sentence or word starts and ends in the audio stream."
    
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='json',
        VoiceId='Joanna',
        SpeechMarkTypes=['word', 'viseme']
    )
    
    marks = response['AudioStream'].read().decode('utf-8')
    with open('polly_output/speech_marks.json', 'w') as f:
        f.write(marks)
    print("Speech marks saved as polly_output/speech_marks.json")

def run_all_experiments():
    print("Starting Amazon Polly experiments...")
    basic_tts()
    ssml_experiment()
    neural_voice_experiment()
    lexicon_experiment()
    speech_marks_experiment()
    print("All experiments completed.")

if __name__ == "__main__":
    run_all_experiments()