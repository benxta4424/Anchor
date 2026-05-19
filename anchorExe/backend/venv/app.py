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
DB_FILE = "mindscan_history.db"

# --- INIȚIALIZARE BAZĂ DE DATE (2 TABELE) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Tabela pentru Persoane / Chaturi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chaturi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume_persoana TEXT DEFAULT 'Anonim',
            data_creare TEXT
        )
    ''')
    
    # 2. Tabela pentru Mesaje (legată de chaturi prin chat_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analize (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            text_manual TEXT,
            text_ocr TEXT,
            scor_risc INTEGER,
            categorie TEXT,
            feedback_ai TEXT,
            data_creare TEXT,
            FOREIGN KEY(chat_id) REFERENCES chaturi(id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ISTORIC EMOTIONAL PENTRU AI ---
def get_recent_scores_context(chat_id):
    """Extrage ultimele scoruri ale persoanei pentru a le da ca context AI-ului"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT scor_risc, categorie, data_creare 
        FROM analize 
        WHERE chat_id = ? 
        ORDER BY id DESC LIMIT 3
    ''', (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "Aceasta este prima evaluare pentru această persoană. Nu există istoric medical recent."
    
    context = "ISTORIC EVOLUȚIE EMOȚIONALĂ RECENTĂ PENTRU ACEASTĂ PERSOANĂ:\n"
    for row in reversed(rows):
        context += f"- La data {row[2]}: Scor Risc {row[0]}% (Categorie: {row[1]})\n"
    context += "Folosește acest istoric pentru a înțelege dacă starea persoanei se agravează, se îmbunătățește sau rămâne critică și adaptează nuanța feedback-ului tău în funcție de evoluție."
    return context


def call_llm_api(text_content, istoric_context):
    """
    Trimite textul curent și istoricul emoțional anterior către Groq API.
    Modelul Llama 3.3 analizează contextul retrospectiv pentru a observa evoluția stării.
    """
    model_name = "llama-3.3-70b-versatile"

    # Prompt clinic avansat cu analiză de trend emoțional
    prompt = f"""
    [AUDIT CLINIC ȘI EVALUARE SEMANTICĂ CU MEMORIE RETROSPECTIVĂ]
    
    CONTEXT ISTORIC (Ultimele stări detectate la acest subiect):
    {istoric_context}
    
    TEXT CURENT DE ANALIZAT: "{text_content}"

    INSTRUCTIUNI DE EVALUARE CONTEXTUALĂ:
    1. Analizează textul curent și bifează indicatorii logici (true/false).
    2. Compară starea din textul curent cu CONTEXTUL ISTORIC primit mai sus.
    3. În câmpul "feedback", oferă o recomandare psihologică caldă, în limba română, 
       care să țină cont de evoluție: dacă starea se agravează, menține-ți fermitatea și compasiunea; 
       dacă starea se îmbunătățește, încurajează subiectul.

    Răspunde STRICT în acest format JSON valid:
    {{
        "analiza_contextuala": "scurt rezumat lingvistic privind evoluția stării față de trecut",
        "text_contine_adio": true/false,
        "text_are_plan_iminent": true/false,
        "text_indica_depresie_cronica": true/false,
        "text_indica_frustrare_stres": true/false,
        "text_are_umor_sau_emoji": true/false,
        "text_este_pozitiv_sau_bucuros": true/false,
        "feedback": "frază de suport psihologic în limba română, adaptată evoluției din istoric"
    }}
    """

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "system", 
                "content": "Ești un psiholog clinician expert și un API determinist. Analizezi evoluția stărilor și răspunzi strict în formatul JSON solicitat."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0,
        "seed": 42,
        "response_format": {"type": "json_object"}
    }

    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            ai_data = json.loads(response.json()['choices'][0]['message']['content'])
            
            # Extragere variabile booleene
            is_adio = ai_data.get("text_contine_adio", False)
            is_iminent = ai_data.get("text_are_plan_iminent", False)
            is_depresie = ai_data.get("text_indica_depresie_cronica", False)
            is_stres = ai_data.get("text_indica_frustrare_stres", False)
            is_umor = ai_data.get("text_are_umor_sau_emoji", False)
            is_pozitiv = ai_data.get("text_este_pozitiv_sau_bucuros", False)

            # Arborele tău de decizie pentru calcularea scorului
            if is_adio and is_iminent and not is_umor:
                score = 100
                category = "URGENȚĂ"
            elif is_adio and not is_umor:
                score = 95
                category = "URGENȚĂ"
            elif is_depresie and not is_umor:
                score = 85
                category = "DEPRESIE"
            elif is_stres:
                score = 55
                if is_umor: 
                    score = 40
                category = "STRES_COTIDIAN"
            elif is_pozitiv:
                score = 10
                category = "POZITIV"
            elif is_umor and not is_depresie and not is_stres:
                score = 25
                category = "POZITIV / NEUTRU"
            else:
                score = 50
                category = "NEUTRU"

            return {
                "thought": ai_data.get("analiza_contextuala", ""),
                "score": score,
                "category": category,
                "feedback": ai_data.get("feedback", "Sunt aici pentru a oferi suport."),
                "indicators": {
                    "is_adio": is_adio,
                    "is_iminent": is_iminent,
                    "is_depresie": is_depresie,
                    "is_stres": is_stres,
                    "is_umor": is_umor
                }
            }
    except Exception as e:
        print(f"Eroare API în urmărirea contextului: {e}")
    
    return {
        "score": 50, 
        "category": "NEUTRU", 
        "feedback": "Sistemul de analiză retrospectivă a întâmpinat o eroare.",
        "indicators": {"is_adio": False, "is_iminent": False, "is_depresie": False, "is_stres": False, "is_umor": False}
    }


# --- ENDPOINT-URI NOI PENTRU GESTIUNE CHATURI ---

@app.route('/create-chat', methods=['POST'])
def create_chat():
    """Creează o persoană nouă (un chat nou). Dacă numele lipsește, devine Anonim."""
    try:
        data = request.json or {}
        nume = data.get('nume', '').strip()
        if not nume:
            nume = "Anonim"
            
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('INSERT INTO chaturi (nume_persoana, data_creare) VALUES (?, ?)', (nume, acum))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"id": new_id, "nume_persoana": nume, "messages": []})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-chats', methods=['GET'])
def get_chats():
    """Returnează lista tuturor persoanelor create"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chaturi ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-chat-messages/<int:chat_id>', methods=['GET'])
def get_chat_messages(chat_id):
    """Încarcă toate mesajele vechi salvate în baza de date pentru o anumită persoană"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM analize WHERE chat_id = ? ORDER BY id ASC', (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        formatted_messages = []
        for r in rows:
            # Reconstruim structura pe care React o folosește pentru a randa bulele
            # Adăugăm mesajul utilizatorului
            if r['text_manual'] or r['text_ocr']:
                formatted_messages.append({
                    "sender": "user",
                    "text": r['text_manual'],
                    "image": None if not r['text_ocr'] else "ocr_present" # flag simplu
                })
            # Adăugăm răspunsul AI asociat
            formatted_messages.append({
                "sender": "ai",
                "text": r['feedback_ai'],
                "score": r['scor_risc'],
                "category": r['categorie']
            })
            
        return jsonify(formatted_messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    try:
        chat_id = request.form.get('chatId')
        if not chat_id:
            return jsonify({"error": "Lipseste chatId. Trebuie sa selectezi o persoana."}), 400

        combined_text = ""
        ocr_text_extracted = ""

        raw_text = request.form.get('rawText', '')
        if raw_text:
            combined_text += f"{raw_text}\n"

        if 'image' in request.files:
            file = request.files['image']
            img = Image.open(io.BytesIO(file.read())).convert('RGB')
            ocr_text_extracted = pytesseract.image_to_string(img, lang='ron+eng')
            combined_text += ocr_text_extracted

        cleaned_text = combined_text.strip()
        if not cleaned_text:
            return jsonify({"error": "Niciun text detectat."}), 400

        # --- EXTRAGEM ISTORICUL PENTRU AI ---
        istoric_context = get_recent_scores_context(chat_id)

        # Apelăm AI-ul trimițând și istoricul precedent
        result = call_llm_api(cleaned_text, istoric_context)
        result['text_ocr'] = ocr_text_extracted.strip()

        # Salvarea în baza de date cu chat_id asociat corect
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO analize (chat_id, text_manual, text_ocr, scor_risc, categorie, feedback_ai, data_creare)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (chat_id, raw_text, result['text_ocr'], result['score'], result['category'], result['feedback'], acum))
            conn.commit()
            conn.close()
            print(f"✓ Salvare reușită pentru chat_id: {chat_id}")
        except Exception as db_err:
            print(f"Eroare stocare DB: {db_err}")

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/delete-chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    try:
        # Folosim fișierul tău real de bază de date definit la începutul scriptului
        conn = sqlite3.connect(DB_FILE) 
        cursor = conn.cursor()
        
        # 1. Ștergem mai întâi toate mesajele (analizele) asociate acestei persoane
        cursor.execute("DELETE FROM analize WHERE chat_id = ?", (chat_id,)) 
        
        # 2. Ștergem persoana din tabela de chaturi
        cursor.execute("DELETE FROM chaturi WHERE id = ?", (chat_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✓ Sesiunea #{chat_id} și istoricul asociat au fost șterse din SQLite.")
        return jsonify({"success": True}), 200
        
    except Exception as e:
        print(f"Eroare la ștergerea chatului: {e}")
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)