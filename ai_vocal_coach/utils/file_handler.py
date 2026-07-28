import tempfile
import os
from contextlib import contextmanager

@contextmanager
def temp_audio_file(uploaded_file):
    """Saves Streamlit UploadedFile to a temp file for Librosa processing, then cleans up."""
    suffix = os.path.splitext(uploaded_file.name)[1] if uploaded_file.name else '.wav'
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        temp_file.write(uploaded_file.read())
        temp_file.close()
        yield temp_file.name
    finally:
        os.unlink(temp_file.name)