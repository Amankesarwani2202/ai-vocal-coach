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

    def _yin_pitch_detection(self, fmin=50, fmax=1000, thr=0.1):
        """YIN pitch detection using autocorrelation."""
        frame_length = int(self.sr / fmin)
        hop_length = max(1, frame_length // 2)
        pitches = []
        times = []

        for start in range(0, len(self.y) - frame_length, hop_length):
            frame = self.y[start:start + frame_length]
            if len(frame) < frame_length:
                break

            acf = np.correlate(frame, frame, mode='full')[len(frame)-1:]
            max_tau = int(self.sr / fmin)
            acf = acf[:max_tau]

            d = np.zeros(len(acf))
            for tau in range(len(acf)):
                d[tau] = np.sum((frame[:-tau if tau > 0 else len(frame)] - frame[tau:]) ** 2) if tau > 0 else 0

            with np.errstate(divide='ignore', invalid='ignore'):
                cmnd = np.divide(d, acf + 1e-8)

            min_tau = int(self.sr / fmax)
            if min_tau < len(cmnd):
                candidates = np.where((cmnd[min_tau:] < thr))[0] + min_tau
                if len(candidates) > 0:
                    tau = candidates[0]
                    if tau > 0:
                        pitch = self.sr / tau
                        pitches.append(pitch)
                        times.append((start + frame_length / 2) / self.sr)
                    else:
                        pitches.append(0)
                else:
                    pitches.append(0)
            else:
                pitches.append(0)

        if not times:
            return np.array([0, self.duration]), np.array([0, 0])

        return np.array(times), np.array(pitches)

    def get_pitch_contour(self, fmin=50, fmax=1000):
        times, pitches = self._yin_pitch_detection(fmin, fmax)
        return times, pitches

    def analyze_stability(self):
        if self.rms.size == 0:
            return 0.0

        amplitude_std = np.std(self.rms)
        amplitude_mean = np.mean(self.rms)
        return 1.0 - min(amplitude_std / (amplitude_mean + 1e-6), 1.0)

    def analyze_breathiness(self):
        return float(np.mean(self.zcr)) if self.zcr.size else 0.0

    def hz_to_note(self, freq):
        """Convert Hz to note name (e.g., 440 Hz → A4)."""
        if freq <= 0:
            return "N/A"
        a4 = 440
        c0 = a4 * pow(2, -4.75)
        h = 12 * np.log2(freq / c0)
        octave = int(h // 12)
        n = int(h % 12)
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return f"{notes[n]}{octave}"

    def detect_range(self, fmin=50, fmax=1000):
        """Detect vocal range from ascending/descending audio."""
        times, pitches = self._yin_pitch_detection(fmin, fmax)
        valid_pitches = pitches[pitches > 0]

        if len(valid_pitches) < 5:
            return None, None, "N/A", "N/A"

        min_pitch = np.min(valid_pitches)
        max_pitch = np.max(valid_pitches)

        return min_pitch, max_pitch, self.hz_to_note(min_pitch), self.hz_to_note(max_pitch)

    def measure_pitch_accuracy(self, target_freq):
        """Measure how close sung pitch is to target (in cents)."""
        if target_freq <= 0:
            return None
        times, pitches = self._yin_pitch_detection()
        valid_pitches = pitches[pitches > 0]

        if len(valid_pitches) == 0:
            return None

        mean_pitch = np.mean(valid_pitches)
        cents_off = 1200 * np.log2(mean_pitch / target_freq)
        return cents_off

    def detect_voiced_frames(self, threshold=0.02):
        """Return percentage of frames with detected pitch (vs unvoiced/silence)."""
        times, pitches = self._yin_pitch_detection()
        voiced = np.sum(pitches > 0)
        return (voiced / len(pitches) * 100) if len(pitches) > 0 else 0

    def measure_pitch_sagging(self, target_freq):
        """Measure percentage of frames below target pitch (pitch sagging)."""
        times, pitches = self._yin_pitch_detection()
        valid_pitches = pitches[pitches > 0]
        if len(valid_pitches) == 0:
            return 0
        below_target = np.sum(valid_pitches < target_freq)
        return (below_target / len(valid_pitches) * 100)

    def measure_pitch_drift(self):
        """Measure pitch stability as std deviation of voiced frames."""
        times, pitches = self._yin_pitch_detection()
        valid_pitches = pitches[pitches > 0]
        if len(valid_pitches) < 2:
            return 0
        return np.std(valid_pitches)

    def measure_interval_size(self, pitch1, pitch2):
        """Measure interval between two pitches in semitones and cents."""
        if pitch1 <= 0 or pitch2 <= 0:
            return 0, 0
        ratio = pitch2 / pitch1
        semitones = 12 * np.log2(ratio)
        cents = semitones * 100
        return semitones, cents

    def detect_register_break(self, threshold_hz=300):
        """Detect sudden pitch jumps (register breaks or cracks)."""
        times, pitches = self._yin_pitch_detection()
        valid_pitches = pitches[pitches > 0]
        if len(valid_pitches) < 2:
            return 0
        diffs = np.abs(np.diff(valid_pitches))
        jumps = np.sum(diffs > threshold_hz)
        return (jumps / len(diffs) * 100) if len(diffs) > 0 else 0

    def measure_breath_consistency(self):
        """Measure consistency of RMS (breath/volume stability)."""
        if self.rms.size < 2:
            return 0
        rms_mean = np.mean(self.rms)
        rms_std = np.std(self.rms)
        consistency = 1.0 - min(rms_std / (rms_mean + 1e-6), 1.0)
        return consistency * 100

    def pitch_within_target_band(self, target_freq, cents_tolerance=50):
        """Return % of time pitch is within tolerance band of target."""
        times, pitches = self._yin_pitch_detection()
        valid_pitches = pitches[pitches > 0]
        if len(valid_pitches) == 0:
            return 0
        cents_off = np.abs(1200 * np.log2(valid_pitches / target_freq))
        within_band = np.sum(cents_off <= cents_tolerance)
        return (within_band / len(valid_pitches) * 100)