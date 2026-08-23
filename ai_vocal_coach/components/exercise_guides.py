"""Exercise-specific visual guides for recording stages."""

import streamlit as st
import streamlit.components.v1 as components


_GUIDES = {
    "range_finder": {
        "title": "Map your comfortable range",
        "label": "Start in the middle, then travel up and down",
        "visual": "range",
    },
    "smooth_onset": {
        "title": "Start each note cleanly",
        "label": "Five light repetitions with no breathy or harsh attack",
        "visual": "onset",
    },
    "legato": {
        "title": "Connect the notes",
        "label": "One continuous line through do - re - mi - re - do",
        "visual": "legato",
    },
    "scale": {
        "title": "Keep every step clear",
        "label": "Do - re - mi - fa - sol on oo with even support",
        "visual": "scale",
    },
    "staccato": {
        "title": "Show the contrast",
        "label": "Separated notes first, connected notes second",
        "visual": "contrast",
    },
    "ear_training": {
        "title": "Match the target",
        "label": "Listen, sing, and settle on the centre",
        "visual": "range",
    },
}


_SVG = {
    "range": '<path class="line range-line" d="M30 105 C75 105 75 45 120 45 S165 105 210 105"/><circle class="dot" cx="30" cy="105" r="7"/><circle class="dot" cx="210" cy="105" r="7"/>',
    "onset": '<path class="line onset-line" d="M30 105 C75 105 85 45 125 45 S170 105 210 105"/>',
    "legato": '<path class="line legato-line" d="M30 110 C70 55 95 55 125 100 S175 145 210 75"/>',
    "scale": '<path class="line scale-line" d="M30 125 L75 105 L120 85 L165 65 L210 45"/><circle class="dot" cx="30" cy="125" r="7"/><circle class="dot" cx="75" cy="105" r="7"/><circle class="dot" cx="120" cy="85" r="7"/><circle class="dot" cx="165" cy="65" r="7"/><circle class="dot" cx="210" cy="45" r="7"/>',
    "contrast": '<path class="line staccato-line" d="M30 125 L55 55 M75 125 L100 55 M120 125 L145 55"/><path class="line legato-line" d="M30 165 C85 140 125 175 210 145"/>',
    "resonance": '<circle class="ring ring-a" cx="120" cy="95" r="58"/><circle class="ring ring-b" cx="120" cy="95" r="35"/><circle class="dot" cx="120" cy="95" r="10"/>',
    "register": '<path class="line register-low" d="M30 135 C75 150 95 115 120 100"/><path class="line register-high" d="M120 100 C145 85 165 50 210 55"/><circle class="dot" cx="120" cy="100" r="8"/>',
    "dynamic": '<path class="line dynamic-line" d="M30 125 C75 125 75 65 120 65 S165 125 210 125"/>',
    "agility": '<path class="line agility-line" d="M30 135 L60 65 L90 125 L120 50 L150 115 L180 45 L210 100"/>',
    "ribbon": '<path class="line ribbon-line" d="M30 115 C70 55 95 150 135 90 S180 45 210 105"/>',
}

for _type, _title, _label, _visual in [
    ("forward_placement", "Bring the tone forward", "Focus the vibration without squeezing", "resonance"),
    ("resonance_colours", "Explore tone colour", "Change the colour, keep the freedom", "resonance"),
    ("mixing_registers", "Blend the registers", "Let the sound lighten through the turn", "register"),
    ("dynamic_shaping", "Shape the dynamic", "Grow and release without losing the pitch", "dynamic"),
    ("messa_di_voce", "Build the arc", "Soft -> full -> soft", "dynamic"),
    ("portamento", "Glide between notes", "Connect the targets without a scoop", "ribbon"),
    ("register_turning_points", "Cross the register", "Release through the turning point", "register"),
    ("ornamentation", "Keep the ornament light", "Quick grace note, steady landing", "agility"),
    ("slow_melismas", "Flow through the melody", "One vowel, many connected notes", "ribbon"),
    ("fast_runs", "Map the fast run", "Accuracy first, then speed", "agility"),
    ("vocalises", "Sing the vocalise", "Let the phrase travel on one breath", "ribbon"),
]:
    _GUIDES[_type] = {"title": _title, "label": _label, "visual": _visual}

for _type, _title, _label in [
    ("repertoire_caro_mio_ben", "Shape the phrase", "Text, breath, and melody move together"),
    ("repertoire_amarilli", "Sing the story", "Clear vowels with a connected line"),
    ("repertoire_folk_song", "Keep it natural", "Simple melody, honest expression"),
    ("repertoire_italian_song", "Carry the line", "Diction stays clear inside the legato"),
    ("repertoire_italian_complete", "Perform the complete song", "Sustain technique from first note to last"),
    ("repertoire_german_lieder", "Speak through the melody", "Crisp text, warm connected tone"),
    ("repertoire_english_song", "Let the words lead", "Understandable text with classical support"),
    ("repertoire_raga_vocalise", "Return to the tonic", "Explore freely, resolve clearly"),
]:
    _GUIDES[_type] = {"title": _title, "label": _label, "visual": "ribbon"}


def render_exercise_guide(exercise_type):
    """Render a large, high-contrast animated visual for a vocal task."""
    guide = _GUIDES.get(exercise_type, {
        "title": "Follow the musical shape",
        "label": "Stay present, supported, and connected",
        "visual": "legato",
    })

    svg = _SVG[guide["visual"]]
    html = f"""
    <style>
      body {{ margin: 0; background: transparent; font-family: Georgia, serif; color: #17201c; }}
      .guide {{ display: grid; grid-template-columns: 1fr 2fr; align-items: center; gap: 1rem;
                padding: 1rem 1.25rem; border: 2px solid #0f766e; border-radius: 12px;
                background: linear-gradient(110deg, #ccfbf1, #fef3c7); }}
      .title {{ font-size: 22px; font-weight: 700; line-height: 1.1; }}
      .label {{ margin-top: .45rem; font: 600 12px/1.35 Arial, sans-serif; color: #115e59; }}
      svg {{ width: 100%; height: 150px; overflow: visible; }}
      .line {{ fill: none; stroke-linecap: round; stroke-linejoin: round; stroke-width: 8; }}
      .range-line, .scale-line {{ stroke: #c2410c; stroke-dasharray: 300; animation: draw 2.2s ease-in-out infinite alternate; }}
      .onset-line {{ stroke: #0f766e; stroke-dasharray: 300; animation: draw 2.2s ease-out infinite alternate; }}
      .legato-line {{ stroke: #2563eb; stroke-dasharray: 300; animation: flow 2.4s linear infinite; }}
      .staccato-line {{ stroke: #dc2626; }}
      .dot {{ fill: #f59e0b; stroke: #7c2d12; stroke-width: 3; animation: pulse 1s ease-in-out infinite alternate; }}
    .ring {{ fill: none; stroke: #0f766e; stroke-width: 8; animation: ring 2s ease-in-out infinite alternate; transform-origin: 120px 95px; }}
    .ring-b {{ stroke: #f59e0b; animation-delay: .35s; }}
    .register-low {{ stroke: #dc2626; }}
    .register-high {{ stroke: #2563eb; }}
    .dynamic-line {{ stroke: #0f766e; stroke-width: 11; animation: breathe 2.4s ease-in-out infinite alternate; }}
    .agility-line {{ stroke: #c2410c; animation: draw 1.3s ease-in-out infinite alternate; }}
    .ribbon-line {{ stroke: #2563eb; stroke-width: 10; animation: flow 2.4s linear infinite; }}
      @keyframes draw {{ from {{ stroke-dashoffset: 300; }} to {{ stroke-dashoffset: 0; }} }}
      @keyframes flow {{ to {{ stroke-dashoffset: -300; }} }}
      @keyframes pulse {{ from {{ transform: scale(.8); transform-origin: center; }} to {{ transform: scale(1.2); transform-origin: center; }} }}
    @keyframes ring {{ from {{ transform: scale(.82); opacity: .65; }} to {{ transform: scale(1.12); opacity: 1; }} }}
    @keyframes breathe {{ from {{ stroke-width: 5; }} to {{ stroke-width: 13; }} }}
      @media (max-width: 600px) {{ .guide {{ grid-template-columns: 1fr; }} .title {{ font-size: 19px; }} svg {{ height: 120px; }} }}
    </style>
    <div class="guide">
      <div><div class="title">{guide["title"]}</div><div class="label">{guide["label"]}</div></div>
      <svg viewBox="0 0 240 190" preserveAspectRatio="none">{svg}</svg>
    </div>
    """
    components.html(html, height=215, scrolling=False)
