import librosa
import numpy as np
import warnings

warnings.filterwarnings('ignore')

class AudioProcessor:
    def __init__(self, file_path: str):
        self.y, self.sr = librosa.load(file_path, sr=None, mono=True)
        if len(self.y) == 0:
            raise ValueError("Audio file is empty.")
            
        self.duration = librosa.get_duration(y=self.y, sr=self.sr)
        self.rms = librosa.feature.rms(y=self.y)[0]
        self.zcr = librosa.feature.zero_crossing_rate(y=self.y)[0]
        
    def get_pitch_contour(self, fmin=50, fmax=1000):
        # Using standard YIN for speed in Streamlit Cloud
        pitches = librosa.yin(self.y, fmin=fmin, fmax=fmax)
        times = librosa.times_like(pitches, sr=self.sr)
        # Clean invalid pitches where energy is low
        mask = self.rms > (np.max(self.rms) * 0.1)
        pitches[~mask[:len(pitches)]] = 0
        return times, pitches

    def analyze_stability(self):
        amplitude_std = np.std(self.rms)
        amplitude_mean = np.mean(self.rms)
        return 1.0 - min(amplitude_std / (amplitude_mean + 1e-6), 1.0)
        
    def analyze_breathiness(self):
        # Higher ZCR often correlates with unvoiced/breathy sounds
        return np.mean(self.zcr)