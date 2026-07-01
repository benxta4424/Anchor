# Enhanced Voice & Face Endpoints - Database Integration

from flask import request, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "mindscan_history.db")

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────

def init_voice_face_db():
    """Initialize voice and face analysis tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS voice_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            transcript TEXT,
            audio_url TEXT,
            voice_score INTEGER,
            energy_score INTEGER,
            pace_score INTEGER,
            clarity_score INTEGER,
            tone_score INTEGER,
            duration REAL,
            features JSON,
            FOREIGN KEY (chat_id) REFERENCES chaturi(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_url TEXT,
            depression_score INTEGER,
            sadness INTEGER,
            anxiety INTEGER,
            irritability INTEGER,
            anhedonia INTEGER,
            dissociation INTEGER,
            dominant_emotion TEXT,
            emotions JSON,
            confidence REAL,
            FOREIGN KEY (chat_id) REFERENCES chaturi(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS multimodal_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            combined_score INTEGER,
            voice_score INTEGER,
            face_score INTEGER,
            text_score INTEGER,
            confidence INTEGER,
            modality_agreement JSON,
            FOREIGN KEY (chat_id) REFERENCES chaturi(id)
        )
    """)
    
    conn.commit()
    conn.close()

# ─── ENDPOINT HANDLERS ─────────────────────────────────────────────────────────

def get_voice_history(chat_id):
    """Get voice analysis history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, transcript, audio_url, voice_score, duration
            FROM voice_analysis
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (chat_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = [
            {
                "id": r[0],
                "timestamp": r[1],
                "transcript": r[2],
                "audio_url": r[3],
                "voice_score": r[4],
                "duration": r[5]
            }
            for r in results
        ]
        
        return jsonify({"status": "success", "history": history}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def get_voice_stats(chat_id):
    """Get voice statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(voice_score) as avg_score,
                MAX(voice_score) as max_score,
                MIN(voice_score) as min_score
            FROM voice_analysis
            WHERE chat_id = ?
        """, (chat_id,))
        
        stats = cursor.fetchone()
        
        cursor.execute("""
            SELECT voice_score
            FROM voice_analysis
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 2
        """, (chat_id,))
        
        recent = cursor.fetchall()
        conn.close()
        
        trend = 0
        if len(recent) == 2:
            trend = recent[0][0] - recent[1][0]
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_recordings": stats[0] or 0,
                "average_score": round(stats[1], 1) if stats[1] else 0,
                "max_score": stats[2] or 0,
                "min_score": stats[3] or 0,
                "trend": trend
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def save_voice_analysis():
    """Save voice analysis"""
    try:
        data = request.json
        chat_id = data.get("chat_id")
        transcript = data.get("transcript")
        voice_score = data.get("voice_score", 0)
        energy_score = data.get("energy_score", 0)
        pace_score = data.get("pace_score", 0)
        clarity_score = data.get("clarity_score", 0)
        tone_score = data.get("tone_score", 0)
        duration = data.get("duration", 0)
        features = data.get("features", {})
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO voice_analysis
            (chat_id, transcript, voice_score, energy_score, pace_score, clarity_score, tone_score, duration, features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, transcript, voice_score, energy_score, pace_score, clarity_score, tone_score, duration, json.dumps(features)))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Voice analysis saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def get_face_history(chat_id):
    """Get face analysis history"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, timestamp, image_url, depression_score, dominant_emotion
            FROM face_analysis
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 20
        """, (chat_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        history = [
            {
                "id": r[0],
                "timestamp": r[1],
                "image_url": r[2],
                "depression_score": r[3],
                "dominant_emotion": r[4]
            }
            for r in results
        ]
        
        return jsonify({"status": "success", "history": history}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def get_emotion_stats(chat_id):
    """Get emotion statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total FROM face_analysis WHERE chat_id = ?
        """, (chat_id,))
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT AVG(depression_score) FROM face_analysis WHERE chat_id = ?
        """, (chat_id,))
        avg_depression = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT MAX(depression_score) FROM face_analysis WHERE chat_id = ?
        """, (chat_id,))
        max_depression = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT dominant_emotion FROM face_analysis WHERE chat_id = ?
            GROUP BY dominant_emotion ORDER BY COUNT(*) DESC LIMIT 1
        """, (chat_id,))
        dominant = cursor.fetchone()
        
        cursor.execute("""
            SELECT depression_score
            FROM face_analysis
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 2
        """, (chat_id,))
        
        recent = cursor.fetchall()
        conn.close()
        
        trend = 0
        if len(recent) == 2:
            trend = recent[0][0] - recent[1][0]
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_analyses": total or 0,
                "average_depression_score": round(avg_depression, 1) if avg_depression else 0,
                "max_depression_score": max_depression or 0,
                "dominant_emotion": dominant[0] if dominant else "N/A",
                "trend": trend
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def save_face_analysis():
    """Save face analysis"""
    try:
        data = request.json
        chat_id = data.get("chat_id")
        depression_score = data.get("depression_score", 0)
        sadness = data.get("sadness", 0)
        anxiety = data.get("anxiety", 0)
        irritability = data.get("irritability", 0)
        anhedonia = data.get("anhedonia", 0)
        dissociation = data.get("dissociation", 0)
        dominant_emotion = data.get("dominant_emotion", "neutral")
        emotions = data.get("emotions", {})
        confidence = data.get("confidence", 0)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO face_analysis
            (chat_id, depression_score, sadness, anxiety, irritability, anhedonia, dissociation, 
             dominant_emotion, emotions, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, depression_score, sadness, anxiety, irritability, anhedonia, dissociation, 
              dominant_emotion, json.dumps(emotions), confidence))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Face analysis saved"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def get_multimodal_stats(chat_id):
    """Get multimodal statistics"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute("SELECT AVG(voice_score) FROM voice_analysis WHERE chat_id = ?", (chat_id,))
        voice_avg = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT AVG(depression_score) FROM face_analysis WHERE chat_id = ?", (chat_id,))
        face_avg = cursor.fetchone()[0] or 0
        
        cursor.execute("""
            SELECT AVG(scor_calculat) FROM analize 
            WHERE chat_id = ? 
              AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
              AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
        """, (chat_id,))
        text_avg = cursor.fetchone()[0] or 0
        
        # Compute a weighted average of active biometrics (Text 50%, Voice 25%, Face 25%)
        weights = []
        vals = []
        if text_avg > 0:
            weights.append(0.5)
            vals.append(text_avg)
        if voice_avg > 0:
            weights.append(0.25)
            vals.append(voice_avg)
        if face_avg > 0:
            weights.append(0.25)
            vals.append(face_avg)
            
        if weights:
            combined = sum(v * w for v, w in zip(vals, weights)) / sum(weights)
        else:
            # Fallback to last text score if averages are 0
            cursor.execute("""
                SELECT scor_calculat FROM analize
                WHERE chat_id = ? AND scor_calculat IS NOT NULL 
                  AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
                  AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
                ORDER BY id DESC LIMIT 1
            """, (chat_id,))
            last_row = cursor.fetchone()
            combined = last_row[0] if last_row else 0
        
        cursor.execute("SELECT tip_detectie FROM chaturi WHERE id = ?", (chat_id,))
        tip_row = cursor.fetchone()
        tip_detectie = tip_row[0] if (tip_row and tip_row[0]) else "mine"
        
        conn.close()
        
        return jsonify({
            "status": "success",
            "stats": {
                "voice_average": round(voice_avg, 1),
                "face_average": round(face_avg, 1),
                "text_average": round(text_avg, 1),
                "combined_average": round(combined, 1),
                "recommendation": get_recommendation(combined),
                "tip_detectie": tip_detectie
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def get_recommendation(score):
    """Generate recommendation based on score"""
    if score < 20:
        return "Stare emotionala buna"
    elif score < 40:
        return "Unele semne de ingrijorare"
    elif score < 60:
        return "Semne moderate de depresie"
    elif score < 80:
        return "Semne semnificative de depresie"
    else:
        return "URGENT! Risc ridicat"


def delete_face_history(chat_id):
    """Delete face analysis history and clean up files from uploads for a chat"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Select all image URLs for this chat to clean up files from disk
        cursor.execute("SELECT image_url FROM face_analysis WHERE chat_id = ?", (chat_id,))
        images = cursor.fetchall()
        
        for row in images:
            img_url = row[0]
            if img_url and "/uploads/" in img_url:
                filename = img_url.split("/uploads/")[-1]
                filepath = os.path.join(os.path.dirname(__file__), "uploads", filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"🗑️ Deleted face snapshot file: {filepath}")
                    except Exception as fe:
                        print(f"⚠️ Failed to delete face snapshot file {filepath}: {fe}")
                        
        cursor.execute("DELETE FROM face_analysis WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Face history and files deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def delete_voice_history(chat_id):
    """Delete voice analysis history and clean up audio files from uploads for a chat"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Select all audio URLs for this chat to clean up files from disk
        cursor.execute("SELECT audio_url FROM voice_analysis WHERE chat_id = ?", (chat_id,))
        recordings = cursor.fetchall()
        
        for row in recordings:
            audio_url = row[0]
            if audio_url and "/uploads/" in audio_url:
                filename = audio_url.split("/uploads/")[-1]
                filepath = os.path.join(os.path.dirname(__file__), "uploads", filename)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"🗑️ Deleted voice recording file: {filepath}")
                    except Exception as fe:
                        print(f"⚠️ Failed to delete voice recording file {filepath}: {fe}")
                        
        cursor.execute("DELETE FROM voice_analysis WHERE chat_id = ?", (chat_id,))
        # Also clean up voice transcripts from the main analize table and reset context
        cursor.execute("DELETE FROM analize WHERE chat_id = ? AND text_manual LIKE '[Mesaj Audio] %'", (chat_id,))
        cursor.execute("DELETE FROM conversation_context WHERE chat_id = ?", (chat_id,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Voice history, audio files, and transcripts deleted successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


def analyze_extended_context(chat_id):
    """
    Extended multimodal context diagnosis.
    Fetches the last N voice, face, and text entries from the database,
    builds a fusion summary, then calls Groq/Llama 3.3 to generate an
    empathetic narrative diagnosis.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # --- Pull recent text analyses ---
        cursor.execute("""
            SELECT text_manual, scor_calculat, data
            FROM analize
            WHERE chat_id = ? AND text_manual IS NOT NULL
              AND text_manual NOT LIKE '[Mesaj Audio] %'
            ORDER BY id DESC LIMIT 5
        """, (chat_id,))
        text_rows = cursor.fetchall()

        # --- Pull recent voice analyses ---
        cursor.execute("""
            SELECT transcript, voice_score, energy_score, pace_score, timestamp
            FROM voice_analysis
            WHERE chat_id = ?
            ORDER BY id DESC LIMIT 5
        """, (chat_id,))
        voice_rows = cursor.fetchall()

        # --- Pull recent face analyses ---
        cursor.execute("""
            SELECT dominant_emotion, depression_score, sadness, anxiety, timestamp
            FROM face_analysis
            WHERE chat_id = ?
            ORDER BY id DESC LIMIT 5
        """, (chat_id,))
        face_rows = cursor.fetchall()

        # --- Pull chat metadata ---
        cursor.execute("SELECT nume_persoana, tip_detectie FROM chaturi WHERE id = ?", (chat_id,))
        meta = cursor.fetchone()
        conn.close()

        if not meta:
            subject_name = "Subiect Anonim"
            detection_type = "mine"
        else:
            subject_name = meta[0] or "Subiect Anonim"
            detection_type = meta[1] or "mine"  # "mine" = self, "apropiat" = close person

        # --- Build context summary ---
        lines = []

        if text_rows:
            lines.append("=== Ultimele mesaje text ===")
            for row in reversed(text_rows):
                score_str = f"{row[1]:.0f}%" if row[1] is not None else "N/A"
                lines.append(f"  [{row[2] or 'N/A'}] Scor risc: {score_str} | Mesaj: \"{(row[0] or '')[:120]}\"")

        if voice_rows:
            lines.append("=== Indicatori vocali recenți ===")
            for row in reversed(voice_rows):
                lines.append(
                    f"  [{row[4] or 'N/A'}] Scor voce: {row[1]}% | Energie: {row[2]}% | Ritm: {row[3]}%"
                    + (f" | Transcriere: \"{(row[0] or '')[:80]}\"" if row[0] else "")
                )

        if face_rows:
            lines.append("=== Indicatori faciali recenți ===")
            for row in reversed(face_rows):
                lines.append(
                    f"  [{row[4] or 'N/A'}] Emoție dominantă: {row[0]} | Scor depresie facială: {row[1]}%"
                    f" | Tristețe: {row[2]}% | Anxietate: {row[3]}%"
                )

        if not text_rows and not voice_rows and not face_rows:
            return jsonify({
                "status": "no_data",
                "message": "Nu există date suficiente pentru o diagnoză extinsă. Adaugă mesaje, înregistrări vocale sau imagini."
            }), 200

        context_block = "\n".join(lines)

        # --- Compute aggregated scores for the prompt ---
        avg_text = sum(r[1] for r in text_rows if r[1] is not None) / max(len(text_rows), 1)
        avg_voice = sum(r[1] for r in voice_rows if r[1] is not None) / max(len(voice_rows), 1)
        avg_face = sum(r[1] for r in face_rows if r[1] is not None) / max(len(face_rows), 1)
        combined = avg_text * 0.5 + avg_voice * 0.25 + avg_face * 0.25

        # --- Build empathy-aware prompt ---
        if detection_type == "mine":
            tone_instruction = (
                "Vorbești DIRECT cu utilizatorul despre propria sa stare. "
                "Fii empatic, cald, subtil. Nu dramatiza și nu speria. "
                "Folosește 'tu' cu grijă. Dacă starea pare bună, spune asta cu căldură."
            )
        else:
            tone_instruction = (
                "Utilizatorul monitorizează o altă persoană dragă. "
                "Fii direct, concis și obiectiv. Oferă observații clare despre ce indică datele. "
                "Evită limbajul alarmist, dar fii clar dacă există semnale îngrijorătoare."
            )

        system_prompt = (
            "Ești un asistent de sănătate mintală cald, empatic și profesionist. "
            "Analizezi date multimodale (text, voce, expresii faciale) și oferi o interpretare umană foarte succintă în limba română, cu diacritice. "
            "Raportul tău trebuie să fie extrem de scurt și concis, limitat la maxim 3-4 propoziții clare. Spune exact ce indică scorul general, de ce este acesta așa și oferă o recomandare esențială. " + tone_instruction
        )

        user_prompt = (
            f"Subiect: {subject_name}\n"
            f"Scor combinat estimat: {combined:.0f}%  "
            f"(text={avg_text:.0f}%, voce={avg_voice:.0f}%, față={avg_face:.0f}%)\n\n"
            f"{context_block}\n\n"
            "Generează un raport foarte scurt conform instrucțiunilor."
        )

        # --- Call Groq LLM ---
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            return jsonify({"status": "error", "error": "GROQ_API_KEY not configured"}), 500

        import requests as req_lib
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.65,
            "max_tokens": 250,
        }
        response = req_lib.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        result = response.json()
        narrative = result["choices"][0]["message"]["content"].strip()

        # Save the combined score and narrative to the analize table
        if chat_id:
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                if combined >= 70:
                    category = "🔴 RISC GENERAL SEVER"
                elif combined >= 40:
                    category = "🟡 RISC GENERAL MODERAT"
                else:
                    category = "🟢 RISC GENERAL SCĂZUT"
                
                cursor.execute("""
                    INSERT INTO analize (chat_id, text_manual, text_ocr, scor_calculat, category,
                                         ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data, feedback)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    "[Analiză Generală Multimodală]", None,
                    round(combined, 1), category,
                    0, 0, 1 if combined >= 40 else 0, 0, 0,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    narrative
                ))
                conn.commit()
                conn.close()
                print("✅ Extended context multimodal analysis saved to database successfully")
            except Exception as db_err:
                print(f"❌ Failed to save extended context analysis: {db_err}")

        return jsonify({
            "status": "success",
            "narrative": narrative,
            "scores": {
                "combined": round(combined, 1),
                "text": round(avg_text, 1),
                "voice": round(avg_voice, 1),
                "face": round(avg_face, 1),
            },
            "data_counts": {
                "text": len(text_rows),
                "voice": len(voice_rows),
                "face": len(face_rows),
            }
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ─── ROUTE REGISTRATION ───────────────────────────────────────────────────────

def register_endpoints(app):
    """Register all endpoints with Flask app"""
    
    @app.route("/get-voice-history/<int:chat_id>", methods=["GET"])
    def route_get_voice_history(chat_id):
        return get_voice_history(chat_id)
    
    @app.route("/get-voice-stats/<int:chat_id>", methods=["GET"])
    def route_get_voice_stats(chat_id):
        return get_voice_stats(chat_id)
    
    @app.route("/save-voice-analysis", methods=["POST"])
    def route_save_voice_analysis():
        return save_voice_analysis()
    
    @app.route("/get-face-history/<int:chat_id>", methods=["GET"])
    def route_get_face_history(chat_id):
        return get_face_history(chat_id)
    
    @app.route("/get-emotion-stats/<int:chat_id>", methods=["GET"])
    def route_get_emotion_stats(chat_id):
        return get_emotion_stats(chat_id)
    
    @app.route("/save-face-analysis", methods=["POST"])
    def route_save_face_analysis():
        return save_face_analysis()
    
    @app.route("/delete-face-history/<int:chat_id>", methods=["DELETE"])
    def route_delete_face_history(chat_id):
        return delete_face_history(chat_id)
    
    @app.route("/delete-voice-history/<int:chat_id>", methods=["DELETE"])
    def route_delete_voice_history(chat_id):
        return delete_voice_history(chat_id)
    
    @app.route("/get-multimodal-stats/<int:chat_id>", methods=["GET"])
    def route_get_multimodal_stats(chat_id):
        return get_multimodal_stats(chat_id)

    @app.route("/analyze-extended-context/<int:chat_id>", methods=["POST"])
    def route_analyze_extended_context(chat_id):
        return analyze_extended_context(chat_id)
