import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from transformers import pipeline
import threading

# Parameters
samplerate = 44100  # Sample rate
duration = 10  # Maximum duration of a recording in seconds
silence_threshold = 0.05  # Silence threshold
filename = "output.mp3"


def record_audio():
    print("Recording...")
    recording = sd.rec(
        int(duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype='float64')
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


def process_audio(file_path):
    # Transcribe the audio fileclea
    result = whisper_pipeline(file_path)
    transcription = result['text']
    print("Transcription:", transcription)


# Loop function
def run_in_loop():
    while True:
        audio_file = record_audio()
        if audio_file:
            threading.Thread(target=process_audio, args=(audio_file,)).start()
