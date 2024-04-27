import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
from pi_voice.config import config

class AudioOperator:
    def __init__(
            self,
            samplerate=44100,
            duration=10,
            silence_threshold=0.05,
            filename=config["audio"]
    ):
        self.samplerate = samplerate
        self.duration = duration
        self.silence_threshold = silence_threshold
        self.filename = filename

    def record_audio(self):
        recording = sd.rec(
            int(self.duration * self.samplerate),
            samplerate=self.samplerate,
            channels=1,
            dtype='float64')
        sd.wait()

        if np.max(recording) < self.silence_threshold:
            return None
        write(self.filename, self.samplerate, recording)
        return self.filename
