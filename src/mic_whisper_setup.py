import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from transformers import pipeline
from googletrans import Translator

# Parameters
samplerate = 44100  # Sample rate
duration = 7  # Maximum duration of a recording in seconds
silence_threshold = 0.05  # Silence threshold
filename = "../output.wav"


def record_audio():
    print("Recording...")
    recording = sd.rec(int(duration * samplerate),
                       samplerate=samplerate, channels=2, dtype='float64')
    sd.wait()
    if np.max(recording) < silence_threshold:
        print("Detected silence, not processing.")
        return None
    print("Recording finished.")
    write(filename, samplerate, recording)
    return filename


# Initialize Whisper model pipeline
whisper_pipeline = pipeline(
    model="openai/whisper-tiny.en", task="automatic-speech-recognition")

# Initialize Google Translate translator
# translator = Translator()


def process_audio(file_path):
    # Transcribe the audio fileclea
    result = whisper_pipeline(file_path)
    transcription = result['text']
    print("Transcription:", transcription)

    # Attempt to detect the language of the transcription
    # detected_language = translator.detect(transcription).lang

    # Translate the transcription to English if it's not already in English
    # if detected_language != 'en':
    #     english_translation = translator.translate(
    #         transcription, src=detected_language, dest='en').text
    #     print(f"Detected Language: {detected_language}")
    #     print("English Translation:", english_translation)
    # else:
    #     print("The transcription is likely in English.")

# Main loop
# while True:
#     audio_file = record_audio()
#     if audio_file:
#         process_audio(audio_file)
