import plotly.graph_objects as go
import numpy as np

def plot_waveform(y: np.ndarray, sr: int):
    times = np.linspace(0, len(y)/sr, num=len(y))
    ds_factor = max(1, len(y) // 5000)
    fig = go.Figure(data=go.Scatter(
        x=times[::ds_factor], y=y[::ds_factor],
        line=dict(color='#00D26A', width=1),
        fill='tozeroy',
        fillcolor='rgba(0, 210, 106, 0.1)'
    ))
    fig.update_layout(
        title="Waveform",
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
        template="plotly_dark",
        xaxis_title="Time (s)",
        yaxis_title="Amplitude",
        hovermode='x unified'
    )
    return fig

def plot_pitch_contour(times: np.ndarray, pitches: np.ndarray):
    valid_idx = pitches > 0
    fig = go.Figure(data=go.Scatter(
        x=times[valid_idx], y=pitches[valid_idx],
        mode='lines+markers',
        line=dict(color='#00D26A', width=2),
        marker=dict(size=4),
        fill='tozeroy',
        fillcolor='rgba(0, 210, 106, 0.1)'
    ))
    fig.update_layout(
        title="Pitch Contour",
        margin=dict(l=20, r=20, t=40, b=20),
        height=250,
        template="plotly_dark",
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        hovermode='x unified'
    )
    return fig

def plot_pitch_vs_target(times: np.ndarray, recorded_pitches: np.ndarray, target_freq: float, label: str = ""):
    """Compare recorded pitch against target pitch."""
    valid_idx = recorded_pitches > 0

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=times[valid_idx], y=recorded_pitches[valid_idx],
        mode='lines',
        name='Your Pitch',
        line=dict(color='#00D26A', width=3)
    ))

    fig.add_hline(
        y=target_freq,
        line_dash="dash",
        line_color="#FF6B9D",
        annotation_text="Target",
        annotation_position="right"
    )

    fig.update_layout(
        title=f"Pitch Tracking {label}",
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template="plotly_dark",
        hovermode='x unified',
        legend=dict(x=0.01, y=0.99)
    )
    return fig

def plot_pitch_stability_gauge(drift_std: float, in_target_pct: float):
    """Create a gauge showing pitch stability metrics."""
    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=in_target_pct,
        title={'text': "In Target Band (%)"},
        domain={'x': [0, 0.45], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#00D26A'},
            'steps': [
                {'range': [0, 33], 'color': '#FFE5E5'},
                {'range': [33, 66], 'color': '#FFF5E5'},
                {'range': [66, 100], 'color': '#E5FFE5'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))

    stability = max(0, 100 - (drift_std / 0.5) * 100)
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=stability,
        title={'text': "Pitch Stability (%)"},
        domain={'x': [0.55, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#00D26A'},
            'steps': [
                {'range': [0, 33], 'color': '#FFE5E5'},
                {'range': [33, 66], 'color': '#FFF5E5'},
                {'range': [66, 100], 'color': '#E5FFE5'}
            ],
            'threshold': {
                'line': {'color': 'red', 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=300,
        template="plotly_dark",
        font=dict(size=12)
    )
    return fig

def plot_radar_score(subscores: dict):
    categories = list(subscores.keys())
    values = list(subscores.values())
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories,
        fill='toself',
        line=dict(color='#00D26A', width=2),
        fillcolor='rgba(0, 210, 106, 0.2)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor='rgba(0, 0, 0, 0.2)'
        ),
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
        height=350,
        template="plotly_dark",
        font=dict(size=11)
    )
    return fig