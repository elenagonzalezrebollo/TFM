import base64, os, tempfile
from datetime import datetime, timedelta
from pathlib import Path
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, jsonify, send_from_directory, current_app)
from flask_login import login_required, current_user
from app import db, csrf 
from app.models import History
from app.utils.audio import save_audio_to_disk, transcribe_and_summarise
from collections import defaultdict
import logging 
import time 

log = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__, template_folder="../templates", static_folder="../static")

@main_bp.context_processor
def inject_histories_by_day():
    if current_user.is_authenticated:
        histories_query = History.query.filter_by(owner=current_user).order_by(History.timestamp.desc()).all()
        histories_by_day_raw = defaultdict(list)
        for h in histories_query:
            histories_by_day_raw[h.timestamp.date()].append(h)

        processed_histories = {}
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)

        for date_obj, items in sorted(histories_by_day_raw.items(), key=lambda x: x[0], reverse=True):
            if date_obj == today:
                display_date = "Hoy"
            elif date_obj == yesterday:
                display_date = "Ayer"
            else:
                if date_obj.year == today.year:
                    display_date = date_obj.strftime("%B %d").capitalize()
                else:
                    display_date = date_obj.strftime("%B %d, %Y").capitalize()
            processed_histories[display_date] = items

        return dict(histories_by_day=processed_histories)
    return dict(histories_by_day=None) 

@main_bp.route("/")
def home(): return redirect(url_for("main.dashboard"))

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# ---------- API ----------
@main_bp.route("/api/upload", methods=["POST"])
@login_required
def upload():
    """
    Carga de los ficheros en distintos formatos sobre recorder.js
    """
    start_time = time.time()
    log.info("<IN> Peticion de carga de fichero")
    try:
        if "file" in request.files:
            f = request.files["file"]
            audio_bytes = f.read()
            filename    = f.filename
            mime        = f.mimetype
            log.info(f"Fichero cargado: {filename}, {mime}, size: {len(audio_bytes)} bytes")
        else:
            data = request.get_json(force=True)
            b64  = data.get("data","")
            audio_bytes = base64.b64decode(b64)
            filename    = data.get("filename","system_audio.webm")
            mime        = data.get("mime","audio/webm")
            log.info(f"JSON cargado: {filename}, {mime}, size: {len(audio_bytes)} bytes")

        saved_rel_path = save_audio_to_disk(audio_bytes, filename)
        log.info(f"Fichero cargado: {saved_rel_path}")

        log.info(f"Comenzando a procesar audio: {saved_rel_path}")
        trans, short, long, display_name = transcribe_and_summarise(saved_rel_path)
        processing_time = time.time() - start_time
        log.info(f"Fichero cargado: {display_name}, tardó: {processing_time:.2f} s")
        
        hist = History(
            filename      = filename,
            display_name  = display_name,
            audio_path    = saved_rel_path,
            audio_mime    = mime,
            transcription = trans,
            summary_short = short,
            summary_long  = long,
            owner         = current_user,
        )
        db.session.add(hist)
        db.session.commit()
        log.info(f"Hsitorificación realizada con ID: {hist.id}")
        
        return jsonify({"ok": True, "history_id": hist.id})
    
    except Exception as e:
        log.error(f"Error al cargar: {str(e)}", exc_info=True)
        return jsonify({"ok": False, "error": str(e)}), 500

@main_bp.route("/history/<history_id>")
@login_required
def history_detail(history_id):
    h = History.query.filter_by(id=history_id, owner=current_user).first_or_404()
    return render_template("history_detail.html", h=h)

@main_bp.route("/download/<path:filename>")
@login_required
def download(filename):
    uploads = current_app.config["AUDIO_DIR"]
    return send_from_directory(uploads, filename, as_attachment=True)

@main_bp.route("/history/delete/<string:history_id>", methods=["POST"])
@login_required
@csrf.exempt  
def delete_history(history_id):
    history_item = History.query.filter_by(id=history_id, owner=current_user).first_or_404()

    if history_item.audio_path:
        try:
            
            audio_file_path = Path(current_app.config["AUDIO_DIR"]) / history_item.audio_path
            if audio_file_path.is_file():
                os.remove(audio_file_path)
                log.info(f"Borrado fichero de audio: {audio_file_path}")
            else:
                log.warning(f"Fichero no encontrado durante el borrado: {audio_file_path}")
        except Exception as e:
            log.error(f"Error al borrar el fichero: {history_item.audio_path}: {e}")
            flash("Error al eliminar el archivo de audio. El registro del historial fue eliminado", "warning") 

    db.session.delete(history_item)
    db.session.commit()
    flash("Elemento del historial eliminado correctamente", "success")
    return redirect(url_for("main.dashboard"))
