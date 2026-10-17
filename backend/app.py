import os, tempfile
from pathlib import Path
from typing import List
import numpy as np
import librosa
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from faster_whisper import WhisperModel

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_FILE = BASE_DIR / "web" / "index.html"
app = FastAPI(title="Song Chord Finder", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=False,
    allow_methods=["*"], allow_headers=["*"]
)

MAX_BYTES = 40 * 1024 * 1024
MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
_whisper = None

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
CHORD_TEMPLATES = {}
for root in range(12):
    major = np.zeros(12); major[[root, (root+4)%12, (root+7)%12]] = 1
    minor = np.zeros(12); minor[[root, (root+3)%12, (root+7)%12]] = 1
    CHORD_TEMPLATES[f"{NOTE_NAMES[root]}"] = major
    CHORD_TEMPLATES[f"{NOTE_NAMES[root]}m"] = minor

def get_whisper():
    global _whisper
    if _whisper is None:
        _whisper = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
    return _whisper

def estimate_chords(y, sr):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=4096)
    frame_seconds = 4096 / sr
    names, times = [], []
    for i in range(chroma.shape[1]):
        v = chroma[:, i]
        norm = np.linalg.norm(v)
        if norm < 1e-7:
            chord = "N"
        else:
            v = v / norm
            scores = {name: float(np.dot(v, template) / (np.linalg.norm(template) + 1e-9))
                      for name, template in CHORD_TEMPLATES.items()}
            chord = max(scores, key=scores.get)
        t = round(i * frame_seconds, 1)
        if not names or names[-1]["chord"] != chord:
            names.append({"time_seconds": t, "chord": chord})
        times.append(t)
    # Collapse tiny repeated changes; keep first estimate at each change.
    return names[:250]

def estimate_key(y, sr):
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    profile = np.mean(chroma, axis=1)
    # Krumhansl-like profiles, sufficient for a rough estimate.
    major_profile = np.array([6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88])
    minor_profile = np.array([6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17])
    best = ("C", -999)
    for shift in range(12):
        for mode, template in [("", major_profile), ("m", minor_profile)]:
            score = float(np.corrcoef(profile, np.roll(template, shift))[0,1])
            if np.isfinite(score) and score > best[1]:
                best = (NOTE_NAMES[shift] + mode, score)
    return best[0]

@app.get("/")
def root():
    if WEB_FILE.exists():
        return FileResponse(WEB_FILE)
    return {"ok": True, "service": "Song Chord Finder API"}

@app.get("/health")
def health():
    return {"ok": True, "service": "Song Chord Finder", "model": MODEL_NAME}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    name = file.filename or "audio"
    ext = Path(name).suffix.lower()
    if ext not in {".mp3", ".wav", ".m4a", ".flac", ".ogg"}:
        raise HTTPException(400, "Supported formats: MP3, WAV, M4A, FLAC, OGG")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty audio file")
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large; maximum is 40 MB")
    suffix = ext if ext else ".audio"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data); temp_path = tmp.name
        y, sr = librosa.load(temp_path, sr=22050, mono=True)
        if len(y) < sr * 2:
            raise HTTPException(400, "Audio is too short")
        duration = float(len(y) / sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        tempo_value = float(np.asarray(tempo).reshape(-1)[0])
        key = estimate_key(y, sr)
        chords = estimate_chords(y, sr)
        try:
            model = get_whisper()
            segments, info = model.transcribe(temp_path, beam_size=3, vad_filter=True)
            lyrics = "\n".join(seg.text.strip() for seg in segments if seg.text.strip())
            language = getattr(info, "language", None)
        except Exception as e:
            lyrics = ""
            language = None
            transcript_error = str(e)[:240]
        else:
            transcript_error = None
        intro = [c for c in chords if c["time_seconds"] <= 15][:12]
        result = {
            "filename": name,
            "duration_seconds": round(duration, 2),
            "tempo_bpm": round(tempo_value, 1),
            "key": key,
            "intro_chords": intro,
            "chords": chords,
            "lyrics": lyrics,
            "transcription_language": language,
            "transcription_error": transcript_error,
            "warning": "Key and chords are automatic estimates. Review them by ear before use."
        }
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)[:300]}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
