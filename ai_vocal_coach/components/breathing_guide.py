"""
Breathing Guide Animation Component
"""

import streamlit as st
import streamlit.components.v1 as components


def render_breathing_guide(exercise_type="warm_up"):
    """Render animated SVG breathing torso with timed breath cues."""

    html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin: 0; padding: 0; background: transparent; font-family: Inter, -apple-system, sans-serif; }
  .wrap { display: flex; flex-direction: column; align-items: center; padding: 12px 0 4px 0; }
  .cue { font-size: 13px; font-weight: 600; color: #B45309; letter-spacing: 0.08em;
         text-transform: uppercase; margin-bottom: 10px; height: 20px; }
  .timer { font-size: 11px; color: #6B6560; margin-top: 6px; }

  .ribs { transform-origin: 90px 130px; animation: ribs 19s ease-in-out infinite; }
  .belly { transform-origin: 90px 175px; animation: belly 19s ease-in-out infinite; }

  @keyframes ribs {
    0%   { transform: scaleX(1); }
    20%  { transform: scaleX(1.18); }
    26%  { transform: scaleX(1.18); }
    100% { transform: scaleX(1); }
  }
  @keyframes belly {
    0%   { transform: scaleY(1); }
    20%  { transform: scaleY(1.12); }
    26%  { transform: scaleY(1.12); }
    100% { transform: scaleY(1); }
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="cue" id="cue">Breathe in</div>

  <svg width="260" height="250" viewBox="0 0 260 250" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="80" y="8" width="20" height="26" rx="8" fill="#E2DDD6" stroke="#B45309" stroke-width="1.5"/>
    <path d="M30 46 Q90 36 150 46 L154 68 Q90 58 26 68 Z" fill="#E2DDD6" stroke="#B45309" stroke-width="1.5"/>
    <g class="ribs">
      <ellipse cx="90" cy="128" rx="52" ry="56" fill="#F8F5F0" stroke="#B45309" stroke-width="1.5"/>
      <path d="M50 104 Q90 99 130 104" stroke="#D4B896" stroke-width="1" fill="none"/>
      <path d="M44 117 Q90 112 136 117" stroke="#D4B896" stroke-width="1" fill="none"/>
      <path d="M42 130 Q90 125 138 130" stroke="#D4B896" stroke-width="1" fill="none"/>
      <path d="M44 143 Q90 138 136 143" stroke="#D4B896" stroke-width="1" fill="none"/>
      <path d="M48 156 Q90 151 132 156" stroke="#D4B896" stroke-width="1" fill="none"/>
      <line x1="90" y1="74" x2="90" y2="173" stroke="#C4A882" stroke-width="1.2"/>
    </g>
    <g class="belly">
      <ellipse cx="90" cy="192" rx="42" ry="30" fill="#F0EDE8" stroke="#B45309" stroke-width="1.5"/>
    </g>
    <path d="M48 173 Q90 183 132 173" stroke="#B45309" stroke-width="1.5" stroke-dasharray="4 3" fill="none"/>
    <text x="145" y="125" font-size="8.5" fill="#B45309" font-family="Inter, sans-serif">ribs expand</text>
    <text x="155" y="136" font-size="8.5" fill="#B45309" font-family="Inter, sans-serif">outward</text>
  </svg>

  <div class="timer" id="timer">4s inhale &rarr; 15s exhale</div>
</div>

<script>
(function() {
  var cue = document.getElementById('cue');
  var timer = document.getElementById('timer');
  var INHALE = 4, TOTAL = 19;
  var start = Date.now();
  function tick() {
    var elapsed = ((Date.now() - start) / 1000) % TOTAL;
    if (elapsed < INHALE) {
      cue.textContent = 'Breathe in';
      timer.textContent = Math.ceil(INHALE - elapsed) + 's';
    } else {
      cue.textContent = 'Release slowly';
      timer.textContent = Math.ceil(TOTAL - elapsed) + 's';
    }
    requestAnimationFrame(tick);
  }
  tick();
})();
</script>
</body>
</html>
"""

    components.html(html, height=340, scrolling=False)

    if exercise_type in ("warm_up", "breath_support"):
        st.markdown("""
- Inhale through your mouth — feel your lower ribs expand outward, not upward
- Keep shoulders completely still
- Exhale with a soft steady "sss" for 15 seconds
        """)

    with st.expander("Check your form"):
        st.markdown("""
**Good signs**
- Shoulders don't rise during the inhale
- Lower ribs expand sideways
- The exhale feels controlled and even, not forced

**Avoid**
- Chest heaving or shoulders lifting
- A noisy gasp on the inhale
- Pushing hard or trailing off at the end
        """)
