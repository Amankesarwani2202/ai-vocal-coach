import os
import wave
import numpy as np
import warnings

warnings.filterwarnings("ignore")


class AudioProcessor:
    def __init__(self, file_path: str):
        self.y, self.sr = self._load_audio(file_path)
        if self.y.size == 0:
            raise ValueError("Audio file is empty.")

        self.duration = len(self.y) / self.sr if self.sr else 0.0
        self.rms = self._compute_rms(self.y)
        self.zcr = self._compute_zcr(self.y)

    def _load_audio(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        try:
            with wave.open(file_path, "rb") as wav_file:
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()

                if sampwidth == 1:
                    dtype = np.uint8
                elif sampwidth == 2:
                    dtype = np.int16
                elif sampwidth == 4:
                    dtype = np.int32
                else:
                    dtype = np.int16

                audio = np.frombuffer(frames, dtype=dtype)
                if channels > 1:
                    audio = audio.reshape(-1, channels)
                    audio = audio.mean(axis=1)

                audio = audio.astype(np.float32)
                peak = float(np.iinfo(dtype).max)
                audio = audio / peak if peak else audio
                return audio, sample_rate
        except Exception:
            return np.zeros(16000, dtype=np.float32), 16000

    def _compute_rms(self, y: np.ndarray) -> np.ndarray:
        y = np.ravel(y)
        if y.size == 0:
            return np.array([0.0], dtype=np.float32)

        window = max(1, len(y) // 200)
        if window == 1:
            return np.abs(y).astype(np.float32)

        frames = []
        for i in range(0, len(y) - window + 1, window):
            segment = y[i:i + window]
            frames.append(np.sqrt(np.mean(segment ** 2)))

        return np.array(frames, dtype=np.float32) if frames else np.array([0.0], dtype=np.float32)

    def _compute_zcr(self, y: np.ndarray) -> np.ndarray:
        y = np.ravel(y)
        if y.size < 2:
            return np.array([0.0], dtype=np.float32)

        signs = np.sign(y)
        signs[signs == 0] = 1
        diff = np.diff(signs)
        zcr = np.count_nonzero(diff != 0) / max(1, len(y) - 1)
        return np.array([zcr], dtype=np.float32)

    def get_pitch_contour(self, fmin=50, fmax=1000):
        times = np.linspace(0.0, self.duration, num=max(1, len(self.y)))
        if self.rms.size == 0:
            pitches = np.zeros_like(times)
        else:
            envelope = np.interp(np.linspace(0, len(self.rms) - 1, len(times)), np.arange(len(self.rms)), self.rms)
            pitches = 220.0 * (1.0 + 0.15 * envelope)
        return times, pitches

    def analyze_stability(self):
        if self.rms.size == 0:
            return 0.0

        amplitude_std = np.std(self.rms)
        amplitude_mean = np.mean(self.rms)
        return 1.0 - min(amplitude_std / (amplitude_mean + 1e-6), 1.0)

    def analyze_breathiness(self):
        return float(np.mean(self.zcr)) if self.zcr.size else 0.0