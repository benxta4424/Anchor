import io
import os
import requests
import json
import urllib3
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Setare cale Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DB_FILE = os.path.join(os.path.dirname(__file__), "mindscan_history.db")

def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chaturi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume_persoana TEXT NOT NULL,
            data_creare TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analize (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text_manual TEXT,
            text_ocr TEXT,
            scor_calculat REAL,
            category TEXT,
            ind_adio INTEGER,
            ind_iminent INTEGER,
            ind_depresie INTEGER,
            ind_stres INTEGER,
            ind_umor INTEGER,
            data TEXT,
            feedback TEXT,
            FOREIGN KEY(chat_id) REFERENCES chaturi(id)
        )
    """)
    conn.commit()
    conn.close()
    print("📊 Baza de date SQLite [mindscan_history.db] a fost inițializată cu succes.")

init_db()

def get_recent_scores_context(chat_id):
    """
    Memorie retrospectivă: Extrage ultimele mesaje și răspunsuri textuale 
    din SQLite pentru ca AI-ul să înțeleagă firul narativ al conversației.
    """
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback, scor_calculat, category 
            FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 4
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Nicio conversație anterioară. Acesta este primul mesaj din sesiune."
        
        rows.reverse()
        
        conversație_istoric = []
        for r in rows:
            user_msg = r[0] if r[0] else (r[1] if r[1] else "[Imagine/Screenshot]")
            ai_reply = r[2]
            scor = r[3]
            cat = r[4]
            
            conversație_istoric.append(f"Utilizator: \"{user_msg}\"")
            conversație_istoric.append(f"AI (Răspuns dat): \"{ai_reply}\" [Scor evaluat atunci: {scor}% - {cat}]")
            
        return "\n".join(conversație_istoric)
    except Exception as e:
        print(f"Eroare la compilarea memoriei textuale: {e}")
        return "Eroare la încărcarea contextului istoric."

def proceseaza_scoring_matematic(ai_data, chat_id):
    # 1. Extragere flag-uri clinice brute
    ind_adio = 1 if ai_data.get("text_contine_adio", False) else 0
    ind_iminent = 1 if ai_data.get("text_are_plan_iminent", False) else 0
    ind_depresie = 1 if ai_data.get("text_indica_depresie_cronica", False) else 0
    ind_stres = 1 if ai_data.get("text_indica_frustrare_stres", False) else 0
    ind_umor = 1 if ai_data.get("text_are_umor_sau_emoji", False) else 0
    ind_pericol_arme = 1 if ai_data.get("text_indica_autoaccidentare_sau_arme", False) else 0
    ind_pozitiv = 1 if ai_data.get("text_este_pozitiv_sau_bucuros", False) else 0
    
    intensitate_base = ai_data.get("scor_intensitate_negativa", 5) * 10.0  # Scara 0-10 -> 0-100
    
    # Verificăm IMEDIAT istoricul din baza de date pentru a vedea dacă pacientul este în "Carantină"
    este_in_carantina_clinica = False
    ultimul_scor_istoric = 0.0
    
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 1", (chat_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            ultimul_scor_istoric = row[0]
            # Dacă ultima evaluare a fost RISC DEPRESIV RIDICAT sau URGENȚĂ CLINICĂ, activăm carantina
            if ultimul_scor_istoric >= 55.0:
                este_in_carantina_clinica = True
    except Exception as e:
        print(f"Eroare la verificarea carantinei: {e}")

    # 2. ALGORITM DE CALIBRARE DINAMICĂ
    scor_calculat = (intensitate_base * 0.4) + (ind_stres * 12.0) + (ind_depresie * 25.0) + (ind_iminent * 40.0) + (ind_adio * 45.0)
    
    # 3. LOGICA DISCRETĂ PENTRU UMOR ȘI POZITIVITATE (Slick Thresholds cu memorie)
    if este_in_carantina_clinica:
        # PENTRU PERSOANELE IN RISC: Fericirea bruscă sau glumele sunt SUSPICIOASE
        if ind_pozitiv or ind_umor:
            # În loc să scădem scorul, îl ținem sus! Aplicăm un efect de amortizare greu
            # AI-ul nu are voie să coboare riscul mai jos de un nivel de veghe (65% din ultimul risc)
            scor_calculat = max(scor_calculat, ultimul_scor_istoric * 0.85)
            print("⚠️ ALERTĂ: Detectată tentativă de mascare sau relaxare suspectă. Scorul rămâne blocat sus.")
        
        if ind_umor:
            scor_calculat += 15.0  # Umorul adăugat pe o stare critică istorică acționează ca un flag de agravare
    else:
        # PENTRU UTILIZATORII ÎN STARE NORMALĂ: Logica standard de reducere a scorului
        if ind_umor and (ind_depresie or ind_iminent or ind_adio):
            scor_calculat += 10.0
        elif ind_umor and ind_pozitiv:
            scor_calculat -= 20.0

    # Forțare critică pentru indicii expliciți de arme sau plan iminent
    if ind_pericol_arme == 1 or (ind_iminent == 1 and ind_adio == 1):
        scor_calculat = max(scor_calculat, 95.0)

    # Constrângere finală interval [0, 100]
    scor_final = max(0.0, min(100.0, scor_calculat))

    # 4. Analiza statistică a abaterii față de Baseline (Media ultimelor 5 intrări)
    trend_analitic = "STARE INIȚIALĂ"
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT scor_calculat FROM analize WHERE chat_id = ? ORDER BY data DESC LIMIT 5", (chat_id,))
        istoric = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if istoric:
            medie_istorica = sum(istoric) / len(istoric)
            deviatie = scor_final - medie_istorica
            if deviatie > 10:
                trend_analitic = f"ALERTĂ: Escaladare critică (+{round(deviatie, 1)}%)"
            elif deviatie < -10:
                trend_analitic = f"OPTIM: Ameliorare statistică (-{round(abs(deviatie), 1)}%)"
            else:
                trend_analitic = "PLATOU STABIL: Parametri recurenți."
    except Exception as e:
        print(f"Eroare statistică: {e}")

    # Clasificarea pe intervale clinice logice
    if scor_final >= 80.0: category = "URGENȚĂ CLINICĂ"
    elif scor_final >= 55.0: category = "RISC DEPRESIV RIDICAT"
    elif scor_final >= 30.0: category = "STRES ȘI ANXIETATE"
    else: category = "STARE GENERALĂ NEUTRĂ"

    return {
        "score": round(scor_final, 1),
        "category": category,
        "trend_analitic": trend_analitic,
        "indicators": {
            "is_adio": bool(ind_adio or ind_pericol_arme), 
            "is_iminent": bool(ind_iminent or ind_pericol_arme),
            "is_depresie": bool(ind_depresie or (este_in_carantina_clinica and ind_pozitiv)), # marcăm depresia dacă e mascată
            "is_stres": bool(ind_stres), 
            "is_umor": bool(ind_umor)
        }
    }

def call_llm_api(text_content, istoric_context):
    prompt = f"""
    [EXPERT PSIHIATRU & ANALIST DE CONTEXT CLINIC]
    
    ISTORICUL RECENT AL CONVERSAȚIEI:
    {istoric_context}
    
    REPLICA NOUĂ DE EVALUAT: "{text_content}"

    MANDAT STRICT PENTRU FEEDBACK (EVITAREA REPETIȚIEI):
    1. ANALIZEAZĂ ce ai răspuns în istoricul de mai sus. Este STRICT INTERZIS să folosești aceleași fraze, structuri sau clișee (cum ar fi "Este important să știi că nu ești singur" sau "oameni care se pot implica"). Schimbă complet vocabularul de la un mesaj la altul!
    2. ADAPTARE PE GRAVITATE:
       - Pentru RISC MEDIU/RIDICAT: Oferă un răspuns cald, scurt (1-2 propoziții), profund uman și personalizat strict pe ce spune (dacă zice de prieteni, vorbește despre conexiuni; dacă se simte o povară, validează-i oboseala). FĂRĂ clișee medicale.
       - Pentru URGENȚĂ CLINICĂ (intenție directă/idei de suicid precum "o sa ma sinucid"): Schimbă tonul instant într-unul ferm, extrem de cald și alarmat. Ex: "Sunt aici cu tine și te ascult, dar te rog din suflet oprește-te. Durerea asta este prea mare ca să o porți singur acum." Păstrează feedback-ul scurt și lasă interfața să pună numerele de urgență.

    INSTRUCTIUNI DE SCORING:
    - "lumea ar fi un loc mai bun fara mine" sau "am ganduri morbide" indică ideatice suicidală pasivă/activă accentuată. Setează 'scor_intensitate_negativa' la un nivel realist de 7 sau 8 (nu îl lăsa blocat la fel ca la stresul de examene).

    Răspunde EXCLUSIV în format JSON valid:
    {{
        "text_contine_adio": true/false,
        "text_are_plan_iminent": true/false,
        "text_indica_depresie_cronica": true/false,
        "text_indica_frustrare_stres": true/false,
        "text_are_umor_sau_emoji": true/false,
        "text_indica_autoaccidentare_sau_arme": true/false,
        "text_este_pozitiv_sau_bucuros": true/false,
        "scor_intensitate_negativa": 0,
        "feedback": "Răspunsul tău empatic, unic și adaptat, complet diferit de replicile tale anterioare."
    }}
    """
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Ești un evaluator clinic avansat care generează structuri JSON fără a repeta niciodată aceleași tipare de text în feedback."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.6,  # CRESCUTĂ de la 0.2 pentru a elimina repetiția mecanică
        "response_format": {"type": "json_object"}
    }
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Eroare Groq la analiza clinică: {e}")
    return None



# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.route("/get-chats", methods=["GET"])
def get_chats():
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nume_persoana, data_creare FROM chaturi ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "nume_persoana": r[1], "data_creare": r[2]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/create-chat", methods=["POST"])
def create_chat():
    try:
        data = request.json
        nume = data.get("nume", "").strip() or "Subiect Anonim"
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chaturi (nume_persoana, data_creare) VALUES (?, ?)", (nume, acum))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"id": new_id, "nume_persoana": nume, "data_creare": acum}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete-chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM analize WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM chaturi WHERE id = ?", (chat_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-chat-messages/<int:chat_id>", methods=["GET"])
def get_chat_messages(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, category, feedback,
                   ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data
            FROM analize WHERE chat_id = ? ORDER BY id ASC
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for r in rows:
            user_text = r[0] if r[0] else r[1]
            history.append({"sender": "user", "text": user_text, "data": r[10]})
            history.append({
                "sender": "ai", "text": r[4], "score": r[2], "category": r[3], "data": r[10],
                "indicators": {
                    "is_adio": bool(r[5]), "is_iminent": bool(r[6]),
                    "is_depresie": bool(r[7]), "is_stres": bool(r[8]), "is_umor": bool(r[9])
                }
            })
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-chat-scores/<int:chat_id>", methods=["GET"])
def get_chat_scores(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT data, scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"data": r[0], "score": r[1], "category": r[2]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/generate-report/<int:chat_id>", methods=["GET"])
def generate_report(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT nume_persoana FROM chaturi WHERE id = ?", (chat_id,))
        p_row = cursor.fetchone()
        if not p_row:
            return jsonify({"error": "Subiect inexistent"}), 404
        
        cursor.execute("SELECT data, scor_calculat, category, ind_adio, ind_iminent, ind_depresie FROM analize WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return jsonify({"status": "DATE INSUFICIENTE", "message": "Sunt necesare minim 2 intrări."}), 200

        log_text = "\n".join([f"Sesiune {i+1} ({r[0]}): Scor={r[1]}%, Clasa={r[2]} [Flags-> Adio:{r[3]}, Iminent:{r[4]}, Depresie:{r[5]}]" for i, r in enumerate(rows)])

        prompt_raportor = f"""
        [SISTEM EXPERT: RAPORT DE EVALUARE TEMPORALĂ]
        Subiect: {p_row[0]}
        Istoric complet:
        {log_text}

        Analizează cronologia datelor de mai sus și extrage fazele dinamice (debut, vârf, remisie) în acest format JSON strict:
        {{
            "punct_debut": "Când și de unde începe degradarea stării conform datelor",
            "faza_critica": "Perioada de vârf/platou a riscului și intensitatea ei",
            "punct_terminare": "Unde se cam termină sau dacă persistă riscul cronic în remisie",
            "prognostic": "Evoluția predictivă pe baza traiectoriei matematice"
        }}
        """
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Ești un analist de date comportamentale care returnează exclusiv structuri JSON."},
                {"role": "user", "content": prompt_raportor}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return jsonify(json.loads(response.json()['choices'][0]['message']['content'])), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    try:
        chat_id = request.form.get("chatId")
        raw_text = request.form.get("rawText", "").strip()
        image_file = request.files.get("image")
        
        if not chat_id:
            return jsonify({"error": "Parametrul chatId este obligatoriu."}), 400
            
        ocr_text = ""
        if image_file:
            img = Image.open(io.BytesIO(image_file.read()))
            ocr_text = pytesseract.image_to_string(img)
            
        working_text = raw_text if raw_text else ocr_text
        if not working_text:
            return jsonify({"error": "Nu s-au detectat date valide."}), 400
            
        istoric_context = get_recent_scores_context(chat_id)
        ai_data = call_llm_api(working_text, istoric_context)
        
        if not ai_data:
            ai_data = {
                "text_contine_adio": False, "text_are_plan_iminent": False, 
                "text_indica_depresie_cronica": False, "text_indica_frustrare_stres": True, 
                "text_are_umor_sau_emoji": False, "text_indica_autoaccidentare_sau_arme": False, 
                "text_este_pozitiv_sau_bucuros": False, "scor_intensitate_negativa": 5, 
                "feedback": "Sistem în recalibrare automată."
            }
            
        rezultat_analiza = proceseaza_scoring_matematic(ai_data, chat_id)
        
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analize (chat_id, text_manual, text_ocr, scor_calculat, category,
                                 ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chat_id, raw_text if raw_text else None, ocr_text if ocr_text else None,
            rezultat_analiza["score"], rezultat_analiza["category"],
            1 if rezultat_analiza["indicators"]["is_adio"] else 0,
            1 if rezultat_analiza["indicators"]["is_iminent"] else 0,
            1 if rezultat_analiza["indicators"]["is_depresie"] else 0,
            1 if rezultat_analiza["indicators"]["is_stres"] else 0,
            1 if rezultat_analiza["indicators"]["is_umor"] else 0,
            acum, ai_data.get("feedback")
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "score": rezultat_analiza["score"],
            "category": rezultat_analiza["category"],
            "feedback": ai_data.get("feedback"),
            "indicators": rezultat_analiza["indicators"],
            "trend_statistic": rezultat_analiza["trend_analitic"]
        }), 200
    except Exception as e:
        print(f"❌ Eroare procesare: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)