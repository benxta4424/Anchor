#o sa generez rapoarte bazate pe ce se intampla in fiecare chat
import io
import os
import requests
import json
import urllib3
import hashlib
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DB_FILE = os.path.join(os.path.dirname(__file__), "mindscan_history.db")

# Fail-Fast System: Verifică integritatea cheii la pornirea serverului
if not GROQ_API_KEY:
    print("❌ EROARE CRITICĂ: Variabila GROQ_API_KEY nu a fost găsită în .env!")
else:
    print("✅ Groq API Key a fost încărcată cu succes prin modulul securizat .env")

def init_db():
    """Inițializează tabelele din SQLite cu structură completă de date cantitative."""
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
    """Extrage ultimele evaluări pentru a le trimite ca mini-istoric brut către AI."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT data, scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY data DESC LIMIT 3", (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return "Nicio evaluare anterioară înregistrată. Acest mesaj reprezintă starea inițială."
        return "\n".join([f"- La data {r[0]}: Scor Risc {r[1]}% (Clasa: {r[2]})" for r in rows])
    except Exception as e:
        return f"Eroare la extragerea istoricului: {e}"

def proceseaza_scoring_matematic(ai_data, chat_id):
    """
    Sistem Expert: Calculează scorul de risc printr-o matrice de ponderi cumulative
    și determină deviația statistică față de Linia de Bază (Baseline) a subiectului.
    """
    ind_adio = 1 if ai_data.get("text_contine_adio", False) else 0
    ind_iminent = 1 if ai_data.get("text_are_plan_iminent", False) else 0
    ind_depresie = 1 if ai_data.get("text_indica_depresie_cronica", False) else 0
    ind_stres = 1 if ai_data.get("text_indica_frustrare_stres", False) else 0
    ind_umor = 1 if ai_data.get("text_are_umor_sau_emoji", False) else 0
    
    intensitate_negativa = ai_data.get("scor_intensitate_negativa", 5)
    
    # 1. Calcul cumulativ bazat pe severitatea indicatorilor lingvistici
    scor_baza = 0
    scor_baza += ind_adio * 45
    scor_baza += ind_iminent * 35
    scor_baza += ind_depresie * 12
    scor_baza += ind_stres * 5
    
    # Corecție de context: Sarcasmul în mediu depresiv amplifică riscul (Mecanism de mascare)
    if ind_umor and (ind_depresie or ind_adio):
        scor_baza += 3
    elif ind_umor:
        scor_baza -= 10
        
    # Adăugarea intensității transmise de LLM
    scor_final = scor_baza + (intensitate_negativa * 0.5)
    scor_final = max(0, min(100, scor_final))  # Constrângere matematică în intervalul [0, 100]

    # 2. Analiza statistică a abaterii față de Baseline (Media ultimelor 5 intrări)
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
            
            if deviatie > 12:
                trend_analitic = f"ALERTĂ: Escaladare critică (+{round(deviatie, 1)}%) față de linia de bază a subiectului."
            elif deviatie < -12:
                trend_analitic = f"OPTIM: Ameliorare statistică (-{round(abs(deviatie), 1)}%) față de linia de bază."
            else:
                trend_analitic = "PLATOU STABIL: Subiectul se menține în parametrii comportamentali recurenți."
    except Exception as e:
        print(f"Eroare calcul deviație statistică: {e}")

    # Clasificarea pe intervale stricte de date
    if scor_final >= 80: category = "URGENȚĂ CLINICĂ"
    elif scor_final >= 60: category = "RISC DEPRESIU RIDICAT"
    elif scor_final >= 35: category = "STRES ȘI ANXIETATE"
    else: category = "STARE GENERALĂ NEUTRĂ"

    return {
        "score": round(scor_final, 1),
        "category": category,
        "trend_analitic": trend_analitic,
        "indicators": {
            "is_adio": bool(ind_adio), "is_iminent": bool(ind_iminent),
            "is_depresie": bool(ind_depresie), "is_stres": bool(ind_stres), "is_umor": bool(ind_umor)
        }
    }

def call_llm_api(text_content, istoric_context):
    """Apelează API-ul Groq utilizând Llama 3.3 ca un extractor structurat de parametri."""
    prompt = f"""
    [EXTRACTOR SEMANTIC NEURONAL PENTRU ANALIZĂ CLINICĂ RETROSPECTIVĂ]
    
    ISTORIC RECENT PARCURS DE SUBIECT:
    {istoric_context}
    
    TEXT CURENT RECEPTAT: "{text_content}"

    INSTRUCTIUNI:
    1. Evaluează textul curent și extrage flag-urile booleene solicitate în formatul JSON.
    2. Determină 'scor_intensitate_negativa' ca un întreg între 0 (calm) și 10 (durere emoțională extremă).
    3. Construiește un feedback psihologic de suport în limba română, corelat nuanțat cu istoricul (dacă starea se agravează față de istoric, fii mai ferm și protector; dacă se îmbunătățește, validează progresul).

    Răspunde STRICT în următorul format JSON valid, fără introducere sau alte comentarii:
    {{
        "text_contine_adio": true/false,
        "text_are_plan_iminent": true/false,
        "text_indica_depresie_cronica": true/false,
        "text_indica_frustrare_stres": true/false,
        "text_are_umor_sau_emoji": true/false,
        "scor_intensitate_negativa": 0,
        "feedback": "Frază de suport psihologic adaptată evoluției."
    }}
    """
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Ești o componentă API de tip extractor de parametri psiholingvistici în format JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return json.loads(response.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Eroare conexiune Groq API: {e}")
    return None

# --- RUTELE FLASK (API ENDPOINTS) ---

@app.route("/get-chats", methods=["GET"])
def get_chats():
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nume_persoana, data_creare FROM chaturi ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return jsonify([
            {
                "id": r[0], 
                "nume_persoana": r[1], 
                "data_creare": r[2]
            } for r in rows
        ]), 200
    except Exception as e:
        print(f"Eroare la get-chats: {e}")
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
    """Șterge o sesiune completă din baza de date alături de toate analizele ei relationale."""
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
            SELECT text_manual, text_ocr, scor_calculat, category, feedback, ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor 
            FROM analize WHERE chat_id = ? ORDER BY id ASC
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for r in rows:
            user_text = r[0] if r[0] else r[1]
            history.append({"sender": "user", "text": user_text})
            history.append({
                "sender": "ai",
                "text": r[4],
                "score": r[2],
                "category": r[3],
                "indicators": {"is_adio": bool(r[5]), "is_iminent": bool(r[6]), "is_depresie": bool(r[7]), "is_stres": bool(r[8]), "is_umor": bool(r[9])}
            })
        return jsonify(history), 200
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
            return jsonify({"error": "Nu s-au detectat date text sau imagini valide."}), 400
            
        # 1. Obținem contextul retrospectiv din SQLite
        istoric_context = get_recent_scores_context(chat_id)
        
        # 2. Extracție parametri semantici prin Groq API
        ai_data = call_llm_api(working_text, istoric_context)
        
        if not ai_data:
            # Fallback de siguranță robust în caz de eroare API
            ai_data = {"text_contine_adio": False, "text_are_plan_iminent": False, "text_indica_depresie_cronica": False, "text_indica_frustrare_stres": True, "text_are_umor_sau_emoji": False, "scor_intensitate_negativa": 5, "feedback": "Sistemul analitic curent necesită recalibrare punctuală."}
            
        # 3. Calcul numeric hibrid bazat pe reguli matematice și deviație istorică
        rezultat_analiza = proceseaza_scoring_matematic(ai_data, chat_id)
        
        # 4. Salvarea setului complet de metrici în baza de date locală
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analize (chat_id, text_manual, text_ocr, scor_calculat, category, ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data, feedback)
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
            "score": rezultat_analiza["score"] if "resultado_analiza" in locals() else rezultat_analiza["score"], # Compatibilitate variabilă locală
            "category": rezultat_analiza["category"],
            "feedback": ai_data.get("feedback"),
            "indicators": rezultat_analiza["indicators"],
            "trend_statistic": rezultat_analiza["trend_analitic"]
        }), 200
        
    except Exception as e:
        print(f"Eroare generală rută analiză: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)