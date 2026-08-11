"""
Simplified Waveform Display Component

Shows audio waveform with feedback markers and clickable timestamps
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


def create_simplified_waveform(audio_data, sample_rate=16000, feedback_markers=None):
    """
    Create a simplified waveform visualization.

    Args:
        audio_data: Numpy array of audio samples
        sample_rate: Sample rate of audio
        feedback_markers: List of dicts with time and label

    Returns:
        Plotly figure
    """
    # Downsample for visualization
    downsample_factor = len(audio_data) // 2000
    if downsample_factor < 1:
        downsample_factor = 1

    downsampled = audio_data[::downsample_factor]
    time_axis = np.arange(len(downsampled)) * downsample_factor / sample_rate

    fig = go.Figure()

    # Main waveform
    fig.add_trace(
        go.Scatter(
            x=time_axis,
            y=downsampled,
            mode="lines",
            name="Recording",
            line=dict(color="rgba(0, 210, 106, 0.8)", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 210, 106, 0.1)",
            hovertemplate="<b>Time:</b> %{x:.2f}s<br><b>Amplitude:</b> %{y:.3f}<extra></extra>",
        )
    )

    # Add feedback markers
    if feedback_markers:
        marker_times = []
        marker_labels = []
        marker_colors = []

        for marker in feedback_markers:
            time = marker.get("time", 0)
            label = marker.get("label", "")
            severity = marker.get("severity", "info")  # info, warning, alert

            marker_times.append(time)
            marker_labels.append(label)

            if severity == "alert":
                marker_colors.append("rgba(220, 53, 69, 0.8)")  # red
            elif severity == "warning":
                marker_colors.append("rgba(255, 193, 7, 0.8)")  # yellow
            else:
                marker_colors.append("rgba(0, 210, 106, 0.8)")  # green

        # Add vertical lines for markers
        for time, label, color in zip(marker_times, marker_labels, marker_colors):
            fig.add_vline(x=time, line_dash="dash", line_color=color, opacity=0.7)

        # Add marker points
        marker_y_values = [
            downsampled[int(t * sample_rate / downsample_factor)]
            if int(t * sample_rate / downsample_factor) < len(downsampled)
            else 0
            for t in marker_times
        ]

        fig.add_trace(
            go.Scatter(
                x=marker_times,
                y=marker_y_values,
                mode="markers+text",
                name="Feedback",
                marker=dict(size=12, color=marker_colors, symbol="circle"),
                text=[f"<b>{l}</b>" for l in marker_labels],
                textposition="top center",
                hovertemplate="<b>%{text}</b><br>Time: %{x:.2f}s<extra></extra>",
            )
        )

    # Update layout
    duration = time_axis[-1] if len(time_axis) > 0 else 0

    fig.update_layout(
        title="Recording Waveform",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        hovermode="x unified",
        plot_bgcolor="rgba(20, 20, 20, 0.9)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(color="rgba(255, 255, 255, 0.8)"),
        height=300,
        margin=dict(l=50, r=20, t=50, b=50),
        xaxis=dict(
            range=[0, duration * 1.05],
            gridcolor="rgba(255, 255, 255, 0.1)",
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.1)",
        ),
        showlegend=False,
    )

    return fig


def render_waveform_with_feedback(audio_data, feedback_markers, sample_rate=16000):
    """
    Render waveform with interactive feedback timeline.

    Args:
        audio_data: Audio samples
        feedback_markers: List of feedback events
        sample_rate: Sample rate
    """
    st.markdown("### 📊 Your Recording")

    fig = create_simplified_waveform(audio_data, sample_rate, feedback_markers)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    # Feedback timeline below
    if feedback_markers:
        st.markdown("### ⏱️ Feedback Events")

        for i, marker in enumerate(feedback_markers):
            time = marker.get("time", 0)
            label = marker.get("label", "")
            severity = marker.get("severity", "info")

            # Color coding
            if severity == "alert":
                icon = "🔴"
                color = "#dc3545"
            elif severity == "warning":
                icon = "🟡"
                color = "#ffc107"
            else:
                icon = "🟢"
                color = "#28a745"

            minutes = int(time // 60)
            seconds = int(time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"

            col1, col2, col3 = st.columns([1, 8, 2])

            with col1:
                st.markdown(f"### {icon}")

            with col2:
                st.markdown(f"**{time_str}** — {label}")

            with col3:
                if st.button(f"Jump", key=f"jump_{i}", use_container_width=True):
                    st.session_state.playback_position = time
                    st.rerun()

            st.markdown("---")


def render_playback_controls():
    """Render audio playback controls."""
    st.markdown("### 🎵 Playback Controls")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("⏮️ Restart", use_container_width=True):
            st.session_state.playback_position = 0

    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.is_playing = False

    with col3:
        if st.button("▶️ Play", use_container_width=True):
            st.session_state.is_playing = True

    with col4:
        if st.button("🔄 Replay", use_container_width=True):
            st.session_state.playback_position = 0
            st.session_state.is_playing = True
