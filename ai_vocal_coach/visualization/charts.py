import plotly.graph_objects as go
import numpy as np

def plot_waveform(y: np.ndarray, sr: int):
    times = np.linspace(0, len(y)/sr, num=len(y))
    # Downsample for faster plotting in browser
    ds_factor = max(1, len(y) // 5000)
    fig = go.Figure(data=go.Scatter(x=times[::ds_factor], y=y[::ds_factor], line=dict(color='#00D26A')))
    fig.update_layout(title="Waveform", margin=dict(l=20, r=20, t=40, b=20), height=200, template="plotly_dark")
    return fig

def plot_pitch_contour(times: np.ndarray, pitches: np.ndarray):
    # Filter unvoiced frames (0 or NaN)
    valid_idx = pitches > 0
    fig = go.Figure(data=go.Scatter(x=times[valid_idx], y=pitches[valid_idx], mode='markers', marker=dict(color='#00D26A', size=4)))
    fig.update_layout(title="Pitch Contour (Hz)", margin=dict(l=20, r=20, t=40, b=20), height=250, template="plotly_dark")
    return fig

def plot_radar_score(subscores: dict):
    categories = list(subscores.keys())
    values = list(subscores.values())
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill='toself', line=dict(color='#00D26A')
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False, margin=dict(l=40, r=40, t=40, b=40), height=300, template="plotly_dark"
    )
    return fig