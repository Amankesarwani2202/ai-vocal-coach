"""
Noise Detection Engine

Detects background noise and alerts user before recording
"""

import numpy as np


def calculate_noise_level(audio_data, sample_rate=16000):
    """
    Calculate noise level from audio.

    Args:
        audio_data: Numpy array of audio samples
        sample_rate: Sample rate

    Returns:
        Dict with noise analysis
    """
    if len(audio_data) == 0:
        return {"noise_level": 0, "quality": "unknown", "recommendation": "No audio data"}

    # Calculate RMS (Root Mean Square)
    rms = np.sqrt(np.mean(audio_data**2))

    # Normalize to 0-1 scale (for 16-bit audio, typical max is ~0.03)
    normalized_rms = min(rms / 0.03, 1.0)

    # Calculate spectral centroid for noise detection
    freqs = np.fft.fftfreq(len(audio_data), 1 / sample_rate)
    magnitudes = np.abs(np.fft.fft(audio_data))
    centroid = np.sum(freqs[: len(freqs) // 2] * magnitudes[: len(magnitudes) // 2]) / (
        np.sum(magnitudes[: len(magnitudes) // 2]) + 1e-8
    )

    # Classify noise level
    noise_level = normalized_rms * 100

    if noise_level < 15:
        quality = "excellent"
        recommendation = "Environment is perfect for recording. You can proceed!"
    elif noise_level < 30:
        quality = "good"
        recommendation = "Background noise is minimal. Recording should be fine."
    elif noise_level < 50:
        quality = "fair"
        recommendation = "Some background noise detected. Try moving to a quieter location."
    else:
        quality = "poor"
        recommendation = "High background noise. You should find a quieter environment."

    return {
        "noise_level": noise_level,
        "quality": quality,
        "recommendation": recommendation,
        "rms": float(rms),
        "spectral_centroid": float(centroid),
    }


def should_allow_recording(noise_analysis, threshold=50):
    """
    Determine if noise level allows recording.

    Args:
        noise_analysis: Output from calculate_noise_level
        threshold: Maximum acceptable noise level

    Returns:
        Bool
    """
    return noise_analysis.get("noise_level", 0) < threshold


def render_noise_warning(noise_analysis):
    """
    Render noise detection warning/approval.

    Args:
        noise_analysis: Output from calculate_noise_level

    Returns:
        None (renders to Streamlit)
    """
    import streamlit as st

    noise_level = noise_analysis.get("noise_level", 0)
    quality = noise_analysis.get("quality", "unknown")
    recommendation = noise_analysis.get("recommendation", "")

    st.markdown("### 🔊 Environment Check")

    # Quality indicator
    if quality == "excellent":
        st.success(f"✅ Noise Level: {noise_level:.1f}% — {recommendation}")
    elif quality == "good":
        st.info(f"✅ Noise Level: {noise_level:.1f}% — {recommendation}")
    elif quality == "fair":
        st.warning(f"⚠️ Noise Level: {noise_level:.1f}% — {recommendation}")
    else:
        st.error(f"🔴 Noise Level: {noise_level:.1f}% — {recommendation}")

    # Progress bar
    st.progress(min(noise_level / 100, 1.0))

    return should_allow_recording(noise_analysis)
