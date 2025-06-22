import os, tempfile, logging, json, re, base64, time
from pathlib import Path
from datetime import datetime
import whisper, torch, ollama
from flask import current_app
from app.config import Config

log = logging.getLogger(__name__)

# ------ Load Ollama model  ------
try:
    log.info("Attempting to load Ollama model (gemma3:4b)...")
    ollama.chat(model="gemma3:4b", messages=[{"role":"system","content":"Initialize"}])
    log.info("Ollama model (gemma3:4b) loaded.")
except Exception as e:
    log.error(f"Failed to pre-load Ollama model (gemma3:4b): {e}")

# ------ Whisper model ------
_device = "cuda" if torch.cuda.is_available() else "cpu"
log.info(f"Using device: {_device}")
_model  = whisper.load_model("small", device=_device)

def save_audio_to_disk(audio_bytes: bytes, original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1] or ".webm"
    stem = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    fname = f"{stem}{ext}"
    full  = Config.AUDIO_DIR / fname
    with open(full, "wb") as f: f.write(audio_bytes)
    log.info(f"Saved audio file: {full}, size: {len(audio_bytes)} bytes")
    return str(fname)  

def _clean(text:str):
    if not text: return ""
    text = re.sub(r'\s+', ' ', text).strip()
    filler = r'\b(eh+|uh+|um+|ahm+|hmm+|bueno|osea|este|pues|vale|entonces|tipo|sabes|como|digo|claro|mira)\b[\s.,!?]*'
    text = re.sub(filler, '', text, flags=re.I)
    return text

def _summaries(text:str):
    if not text or text.lower().startswith("error"):
        return "N/A", "N/A", "N/A"
    text = _clean(text)
    
    short = "Error al generar resumen corto" 
    long = "Error al generar resumen detallado" 
    display_name = "Error al generar nombre" 

    try:
        
        log.info("Generating short summary...")
        start_time = time.time()
        msg1 = [
          {"role":"system","content":"Eres un experto en resumir textos en 1-2 frases, (SOLO DEVUELVE EL RESUMEN, SIN NINGUN TEXTO ADICIONAL)."},
          {"role":"user",  "content":f"Resume en máximo dos frases:\\n{text}\\n\\n Eres un experto en resumir textos en 1-2 frases, (SOLO DEVUELVE EL RESUMEN, SIN NINGUN TEXTO ADICIONAL)."},
        ]
        short = ollama.chat(model="gemma3:4b", messages=msg1)["message"]["content"].strip()
        log.info(f"Short summary generated in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        log.error(f"Ollama failed for short summary: {e}")

    try:
        
        log.info("Generating detailed summary...")
        start_time = time.time()
        msg2 = [
          {"role":"system","content":"Eres un experto en resumir detalladamente. Haz un resumen detallado del texto proporcionado por el usuario (hasta 2000 caracteres, en texto plano, puede tener saltos de línea, sin negrita, sin formato de .md, en español si el texto es en español)(SOLO DEVUELVE EL RESUMEN, SIN NINGUN TEXTO ADICIONAL)."},
          {"role":"user","content":f"Resumir el siguiente texto:\\n{text} \\n\\n Eres un experto en resumir detalladamente. Haz un resumen detallado del texto proporcionado por el usuario (hasta 2000 caracteres, en texto plano, puede tener saltos de línea, sin negrita, sin formato de .md, en español si el texto es en español)(SOLO DEVUELVE EL RESUMEN, SIN NINGUN TEXTO ADICIONAL)."},
        ]
        long  = ollama.chat(model="gemma3:4b", messages=msg2)["message"]["content"].strip()
        log.info(f"Long summary generated in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        log.error(f"Ollama failed for long summary: {e}")

    try:
        log.info("Generating display name...")
        start_time = time.time()
        msg3 = [
            {"role": "system", "content": "Eres un experto en dar nombres cortos y descriptivos a textos, de 2 a 3 palabras. SOLO DEVUELVE EL NOMBRE, SIN NINGUN TEXTO ADICIONAL."},
            {"role": "user", "content": f"Dame el tema del que esta hablando en solo 2 a 3 palabras (en texto plano, maximo 3 palabras de respuesta, solo responde con el tema) para el siguiente texto:\\n{text} \\n\\n Eres un experto en dar nombres cortos y descriptivos a textos, de 2 a 3 palabras. SOLO DEVUELVE EL NOMBRE, SIN NINGUN TEXTO ADICIONAL."},
        ]
        display_name = ollama.chat(model="gemma3:4b", messages=msg3)["message"]["content"].strip()
        log.info(f"Display name generated in {time.time() - start_time:.2f} seconds: {display_name}")
    except Exception as e:
        log.error(f"Ollama failed for display name: {e}")
        
    return short, long, display_name

def transcribe_and_summarise(rel_path:str):
    full_path = Config.AUDIO_DIR / rel_path
    transcription_start = time.time()
    log.info(f"Starting transcription of {rel_path}")
    print(f"Starting transcription of {full_path}")
    try:
        with tempfile.NamedTemporaryFile(suffix=full_path.suffix, delete=False) as tmp:
            tmp.write(full_path.read_bytes()); tmp_path = tmp.name
        fp16 = (_device=="cuda")
        log.info(f"Transcribing with Whisper on {_device}, fp16={fp16}")
        print(f"Transcribing with Whisper on {_device}, fp16={fp16}")
        result = _model.transcribe(tmp_path, language="es", fp16=fp16)
        print(result)
        text = result["text"].strip() or "Transcripción vacía/silencio."
        log.info(f"Transcription completed in {time.time() - transcription_start:.2f} seconds. Text length: {len(text)} characters")
    except Exception as e:
        text = f"Error: {e}"
        log.exception("Whisper failed")
    finally:
        try: os.remove(tmp_path)
        except: pass
    
    summary_start = time.time()
    log.info("Starting summarization process...")
    short, long, display_name = _summaries(text)
    log.info(f"Summarization completed in {time.time() - summary_start:.2f} seconds")
    
    return text, short, long, display_name
