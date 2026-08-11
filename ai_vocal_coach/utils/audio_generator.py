"""
Audio Exemplar Generator

Generates synthetic audio exemplars for all exercises
"""

import numpy as np
import wave
import io


def generate_tone(frequency, duration=2.0, sr=16000, volume=0.3):
    """Generate a sine wave tone."""
    t = np.linspace(0, duration, int(sr * duration), False)
    audio = np.sin(2 * np.pi * frequency * t) * volume
    return audio


def generate_ss_sound(duration=15.0, sr=16000, volume=0.2):
    """Generate a steady 'sss' breath sound."""
    t = np.linspace(0, duration, int(sr * duration), False)
    # White noise filtered to simulate 'sss' (high frequency)
    noise = np.random.normal(0, 1, len(t))
    # Simple high-pass filter effect
    audio = noise * volume
    return audio


def generate_exemplar_audio(exercise_id, sr=16000):
    """Generate exemplar audio for an exercise."""

    if exercise_id == "0_1_warm_up":
        # Warm-up: Three notes on a comfortable pitch
        audio = np.array([])
        for _ in range(3):
            # 2-second tone
            audio = np.concatenate([audio, generate_tone(440, 2.0, sr, 0.3)])
            # 1-second silence
            audio = np.concatenate([audio, np.zeros(sr)])
        return audio

    elif exercise_id == "0_2_range_finder":
        # Range finder: Ascending scale
        audio = np.array([])
        notes = [261.63, 293.66, 329.63, 349.23, 392.00]  # C-D-E-F-G
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 2.0, sr, 0.3)])
            audio = np.concatenate([audio, np.zeros(int(0.5*sr))])
        return audio

    elif exercise_id == "0_3_ear_training":
        # Ear training: Match three pitches
        audio = np.array([])
        pitches = [440, 494.88, 523.25]  # A, B, C
        for pitch in pitches:
            audio = np.concatenate([audio, generate_tone(pitch, 1.5, sr, 0.3)])
            audio = np.concatenate([audio, np.zeros(int(0.5*sr))])
        return audio

    elif exercise_id == "1_1_diaphragmatic":
        # Diaphragmatic: Steady 'sss' for 15 seconds
        audio = generate_ss_sound(15.0, sr, 0.2)
        return audio

    elif exercise_id == "1_2_silent_breath":
        # Silent breath: 5 seconds of breath sound
        audio = generate_ss_sound(5.0, sr, 0.15)
        return audio

    elif exercise_id == "1_3_smooth_onset":
        # Smooth onset: Gentle attack on a note
        audio = np.array([])
        t = np.linspace(0, 2, 2*sr, False)
        # Soft attack envelope
        envelope = np.where(t < 0.5, t/0.5, 1.0)
        tone = np.sin(2 * np.pi * 440 * t) * envelope * 0.3
        audio = np.concatenate([audio, tone])
        return audio

    elif exercise_id == "1_4_legato":
        # Legato: Three connected notes
        audio = np.array([])
        notes = [440, 494.88, 523.25]  # A, B, C
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 2.0, sr, 0.3)])
        return audio

    elif exercise_id == "1_5_five_note_scale":
        # Five-note scale: Do-re-mi-fa-sol
        audio = np.array([])
        notes = [261.63, 293.66, 329.63, 349.23, 392.00]  # C-D-E-F-G
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 1.5, sr, 0.3)])
        return audio

    elif exercise_id == "1_6_staccato_legato":
        # Staccato vs Legato: Demonstrate both
        audio = np.array([])
        # Staccato: short notes
        for _ in range(3):
            audio = np.concatenate([audio, generate_tone(440, 0.5, sr, 0.3)])
            audio = np.concatenate([audio, np.zeros(int(0.5*sr))])
        # Legato: connected notes
        for _ in range(3):
            audio = np.concatenate([audio, generate_tone(440, 1.0, sr, 0.3)])
        return audio

    elif exercise_id == "2_1_major_ascending":
        # Major scale ascending: Full octave
        audio = np.array([])
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C-D-E-F-G-A-B-C
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 1.5, sr, 0.3)])
        return audio

    elif exercise_id == "2_2_major_descending":
        # Major scale descending
        audio = np.array([])
        notes = [523.25, 493.88, 440.00, 392.00, 349.23, 329.63, 293.66, 261.63]  # C-B-A-G-F-E-D-C (descending)
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 1.5, sr, 0.3)])
        return audio

    elif exercise_id == "2_3_minor_scales":
        # Natural minor scale: A minor
        audio = np.array([])
        notes = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00]  # A-B-C-D-E-F-G-A
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 1.5, sr, 0.3)])
        return audio

    elif exercise_id == "2_4_intervals":
        # Interval training: Various intervals
        audio = np.array([])
        intervals = [(440, 523.25), (440, 587.33), (440, 659.25), (440, 783.99)]  # Major 3rd, 4th, 5th, 6th
        for freq1, freq2 in intervals:
            audio = np.concatenate([audio, generate_tone(freq1, 1.0, sr, 0.3)])
            audio = np.concatenate([audio, generate_tone(freq2, 1.0, sr, 0.3)])
            audio = np.concatenate([audio, np.zeros(int(0.5*sr))])
        return audio

    elif exercise_id == "2_5_arpeggios":
        # Arpeggios: C major triad
        audio = np.array([])
        notes = [261.63, 329.63, 392.00, 523.25]  # C-E-G-C (arpeggio)
        for note in notes:
            audio = np.concatenate([audio, generate_tone(note, 1.0, sr, 0.3)])
        return audio

    elif exercise_id == "2_6_pitch_stability":
        # Pitch stability: 8-second sustained note
        audio = generate_tone(440, 8.0, sr, 0.3)
        return audio

    else:
        # Default: 5-second tone
        return generate_tone(440, 5.0, sr, 0.3)


def save_exemplar_to_file(exercise_id, filepath, sr=16000):
    """Generate and save exemplar audio to WAV file."""
    audio = generate_exemplar_audio(exercise_id, sr)

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.9

    # Convert to 16-bit PCM
    audio_int16 = np.int16(audio * 32767)

    # Write to WAV file
    with wave.open(filepath, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        wav_file.writeframes(audio_int16.tobytes())


def generate_all_exemplars(output_dir):
    """Generate all 15 exercise exemplars."""
    exercise_ids = [
        "0_1_warm_up",
        "0_2_range_finder",
        "0_3_ear_training",
        "1_1_diaphragmatic",
        "1_2_silent_breath",
        "1_3_smooth_onset",
        "1_4_legato",
        "1_5_five_note_scale",
        "1_6_staccato_legato",
        "2_1_major_ascending",
        "2_2_major_descending",
        "2_3_minor_scales",
        "2_4_intervals",
        "2_5_arpeggios",
        "2_6_pitch_stability",
    ]

    for exercise_id in exercise_ids:
        filepath = f"{output_dir}/{exercise_id}.wav"
        save_exemplar_to_file(exercise_id, filepath)
        print(f"✅ {exercise_id}.wav")
