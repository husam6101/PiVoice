from transformers import pipeline
import threading
from pi_voice.operators import logger


class WhisperOperator:
    def __init__(self, model="openai/whisper-tiny.en"):
        self.whisper_pipeline = pipeline(
            model=model, task="automatic-speech-recognition")

    def process(self, audio):
        if audio:
            result = self.whisper_pipeline(audio)
            transcription = result['text']
            return transcription


class ContinuousOperator:
    def __init__(self, recorder, processor):
        self.recorder = recorder
        self.processor = processor

    def run_in_loop(self):
        while True:
            audio_file = self.recorder.record_audio()
            if audio_file:
                threading.Thread(
                    target=self.processor.process_audio, args=(audio_file,)
                ).start()
