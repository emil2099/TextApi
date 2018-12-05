import io
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Ekalimullin/Desktop/Python Projects/flask_api/app/static/speech-to-text-f40318fcbc23.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/Ekalimullin/Desktop/Python Projects/flask_api/app/static/speech-to-text-1543854082123-6553574168d8.json'

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# Instantiates a client
client = speech.SpeechClient()

# The name of the audio file to transcribe
file_name = 'C:/Users/Ekalimullin/Desktop/Python Projects/flask_api/app/static/wav/demo-sample-1-short.wav'

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)

speech_config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    language_code='en-US',
    use_enhanced=True,
    # A model must be specified to use enhanced model.
    model='phone_call',
    enable_automatic_punctuation=True)

# Detects speech in the audio file
response = client.recognize(speech_config, audio)

for result in response.results:
    print('Transcript: {}'.format(result.alternatives[0].transcript))

transcript = ' '.join(result.alternatives[0].transcript for result in response.results)

print('Full transcript: {}'.format(transcript))