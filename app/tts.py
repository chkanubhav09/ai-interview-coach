# app/tts.py
# Text-to-speech module using gTTS

import base64
import hashlib
import os
import tempfile
from pathlib import Path
from gtts import gTTS

CACHE_DIR = Path(tempfile.gettempdir()) / "interview_tts_cache"
CACHE_DIR.mkdir(exist_ok=True)


class TextToSpeech:
    """Converts text to speech audio using gTTS with file-based caching."""

    def __init__(self, lang: str = "en", slow: bool = False):
        self._lang = lang
        self._slow = slow

    def _cache_path(self, text: str) -> Path:
        key = hashlib.md5(text.encode()).hexdigest()
        return CACHE_DIR / f"{key}.mp3"

    async def synthesize_file(self, text: str) -> str:
        """Return path to MP3 audio file for the given text."""
        path = self._cache_path(text)
        if not path.exists():
            tts = gTTS(text=text[:500], lang=self._lang, slow=self._slow)
            tts.save(str(path))
        return str(path)

    async def synthesize_b64(self, text: str) -> str:
        """Return base64-encoded MP3 audio string for inline playback."""
        path = await self.synthesize_file(text)
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def clear_cache(self):
        """Remove all cached TTS files."""
        for f in CACHE_DIR.glob("*.mp3"):
            f.unlink(missing_ok=True)
