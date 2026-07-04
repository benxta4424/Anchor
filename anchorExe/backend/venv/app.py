import io
import os
import requests
import json
import urllib3
import sqlite3
import base64
from datetime import datetime
from collections import Counter
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import pytesseract

# Try to install python-dotenv if missing
try:
    import dotenv
except ImportError:
    import subprocess
    import sys
    print("📦 Installing python-dotenv...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv", "-q"])
        print("✅ python-dotenv installed")
    except Exception as e:
        print(f"❌ Failed to install python-dotenv: {e}")

# Load environment variables from multiple possible paths
try:
    from dotenv import load_dotenv
    loaded = False
    for path in [
        os.path.join(os.path.dirname(__file__), '.env'),
        os.path.join(os.path.dirname(__file__), '..', '.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    ]:
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            load_dotenv(abs_path)
            print(f"✅ Loaded environment variables from: {abs_path}")
            loaded = True
    
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        print(f"🔑 GROQ_API_KEY is successfully loaded (starts with: {api_key[:8]}...)")
    else:
        print("🚨 WARNING: GROQ_API_KEY is NOT set in environment variables! Please check your .env file.")
        
except Exception as e:
    print(f"⚠️ Failed to load environment variables: {e}")

# Try to install numpy, groq and librosa if missing (for voice/face modules)
for package in ["numpy", "groq", "librosa"]:
    try:
        __import__(package)
    except ImportError:
        import subprocess
        import sys
        print(f"📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
            print(f"✅ {package} installed")
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")

# Import voice and face modules separately
VOICE_ENABLED = False
FACE_ENABLED = False

try:
    from voice import process_voice_input
    VOICE_ENABLED = True
    print("✅ Voice module loaded successfully")
except Exception as e:
    print(f"⚠️ Voice module not available: {e}")

try:
    from face import process_face_input, combine_voice_and_face_scores
    FACE_ENABLED = True
    print("✅ Face module loaded successfully")
except Exception as e:
    print(f"⚠️ Face module not available: {e}")

# Import enhanced endpoints for voice/face database integration
try:
    from enhanced_endpoints_new import register_endpoints, init_voice_face_db
    print("✅ Enhanced Voice/Face endpoints loaded")
except ImportError as e:
    print(f"⚠️ Enhanced endpoints not available: {e}")
    register_endpoints = None
    init_voice_face_db = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# Add static uploads folder and file serving route
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOADS_DIR, filename)

def save_base64_file(data_url, prefix, extension):
    import time
    if not data_url:
        return None
    try:
        if ',' in data_url:
            header, encoded = data_url.split(',', 1)
        else:
            encoded = data_url
        data = base64.b64decode(encoded)
        filename = f"{prefix}_{int(time.time() * 1000)}.{extension}"
        filepath = os.path.join(UPLOADS_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(data)
        return f"http://localhost:5000/uploads/{filename}"
    except Exception as e:
        print(f"Error saving base64 file: {e}")
        return None

# Initialize databases first
try:
    if init_voice_face_db:
        init_voice_face_db()
        print("✅ Voice/Face database initialized")
except Exception as e:
    print(f"⚠️ Failed to initialize voice/face database: {e}")

# Check and copy face-api models from node_modules to public/models if missing
try:
    import shutil
    node_modules_models = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "node_modules", "@vladmandic", "face-api", "model"))
    public_models = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "public", "models"))
    
    if os.path.exists(node_modules_models):
        os.makedirs(public_models, exist_ok=True)
        copied_count = 0
        for file_name in os.listdir(node_modules_models):
            src_file = os.path.join(node_modules_models, file_name)
            dst_file = os.path.join(public_models, file_name)
            if not os.path.exists(dst_file) and os.path.isfile(src_file):
                shutil.copy2(src_file, dst_file)
                copied_count += 1
        if copied_count > 0:
            print(f"✅ Copied {copied_count} face-api model weights to public/models")
    else:
        print("⚠️ Face-API model weights not found in node_modules")
except Exception as e:
    print(f"⚠️ Failed to check/copy face-api models: {e}")

# Register enhanced endpoints after database is ready
try:
    if register_endpoints:
        register_endpoints(app)
        print("✅ Enhanced endpoint routes registered")
except Exception as e:
    print(f"⚠️ Failed to register endpoints: {e}")

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DB_FILE = os.path.join(os.path.dirname(__file__), "mindscan_history.db")


# ─── DATABASE ─────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chaturi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume_persoana TEXT NOT NULL,
            data_creare TEXT NOT NULL,
            tip_detectie TEXT DEFAULT 'mine'
        )
    """)
    # Run dynamic migration in case table already existed without tip_detectie
    try:
        cursor.execute("PRAGMA table_info(chaturi)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'tip_detectie' not in columns:
            cursor.execute("ALTER TABLE chaturi ADD COLUMN tip_detectie TEXT DEFAULT 'mine'")
            conn.commit()
            print("🚀 Successfully migrated chaturi: added tip_detectie column")
    except Exception as me:
        print(f"⚠️ Migration warning (tip_detectie): {me}")

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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            emotional_trajectory TEXT,
            pattern_markers TEXT,
            linguistic_markers TEXT,
            sarcasm_detected INTEGER,
            last_emotional_state TEXT,
            FOREIGN KEY(chat_id) REFERENCES chaturi(id)
        )
    """)
    conn.commit()
    conn.close()
    print("📊 Baza de date SQLite [mindscan_history.db] a fost inițializată cu succes.")

init_db()

# Diagnostic Database Dumper & Live Groq Model Fetcher
try:
    import sqlite3
    import os
    import requests
    db_path = os.path.join(os.path.dirname(__file__), "mindscan_history.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    dump_path = os.path.join(os.path.dirname(__file__), "debug_db_dump.txt")
    
    # Fetch live models from Groq
    groq_models = []
    if GROQ_API_KEY:
        try:
            r = requests.get("https://api.groq.com/openai/v1/models", headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, timeout=10)
            if r.status_code == 200:
                data = r.json()
                groq_models = [m["id"] for m in data.get("data", [])]
            else:
                groq_models = [f"API Error {r.status_code}: {r.text[:200]}"]
        except Exception as api_err:
            groq_models = [f"API Connection Exception: {api_err}"]
    else:
        groq_models = ["No API Key available"]

    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("=== LIVE GROQ MODELS ===\n")
        for model in groq_models:
            f.write(f"- {model}\n")
        f.write("\n")
        f.write("=== DATABASE TABLES ===\n")
        f.write(f"Tables in DB: {tables}\n\n")
        if "face_analysis" in tables:
            c.execute("SELECT id, chat_id, timestamp, depression_score, dominant_emotion, confidence FROM face_analysis ORDER BY id DESC LIMIT 10")
            rows = c.fetchall()
            f.write("Latest face_analysis entries:\n")
            for r in rows:
                f.write(f"ID={r[0]}, ChatID={r[1]}, Time={r[2]}, Score={r[3]}, Emotion={r[4]}, Confidence={r[5]}\n")
        else:
            f.write("face_analysis table not found!\n")
    conn.close()
    print("📢 Live Groq models and DB dump written to debug_db_dump.txt")
except Exception as e:
    print(f"⚠️ Diagnostic DB dump failed: {e}")

# Initialize voice and face analysis tables
if init_voice_face_db:
    try:
        init_voice_face_db()
        print("✅ Voice/Face database tables initialized successfully")
    except Exception as e:
        print(f"⚠️ Voice/Face database initialization: {e}")


# ─── CONTEXT ISTORIC ──────────────────────────────────────────────────────────

def get_extended_context(chat_id):
    """Returnează context extins cu analiza emoțională și pattern-uri."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback, scor_calculat, category, data
            FROM analize 
            WHERE chat_id = ? 
              AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
              AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
            ORDER BY id DESC LIMIT 10
        """, (chat_id,))
        rows = cursor.fetchall()
        
        cursor.execute("""
            SELECT emotional_trajectory, pattern_markers, linguistic_markers, last_emotional_state
            FROM conversation_context WHERE chat_id = ? ORDER BY id DESC LIMIT 1
        """, (chat_id,))
        context_row = cursor.fetchone()
        conn.close()
        
        if not rows:
            return "Acesta este primul mesaj din această sesiune."
        
        rows.reverse()
        lines = []
        
        for r in rows:
            user_msg = r[0] or r[1] or "[imagine]"
            score = r[3]
            category = r[4]
            
            lines.append(f'[{r[5]}] Utilizator: "{user_msg}"')
            lines.append(f'Răspuns: scor={score}% ({category})')
        
        context_str = "\n".join(lines)
        
        if context_row:
            context_str += f"\n\n📊 ISTORIC EMOȚIONAL:\nTraiectorie: {context_row[0]}\nPattern-uri: {context_row[1]}\nMarkeri lingvistici: {context_row[2]}\nStare recentă: {context_row[3]}"
        
        return context_str
    except Exception as e:
        print(f"Eroare context extins: {e}")
        return "Context indisponibil."


def analyze_linguistic_markers(text):
    markers = {
        "depression_markers": [],
        "sarcasm_indicators": [],
        "exaggeration_markers": [],
        "hope_markers": []
    }
    
    text_lower = text.lower()
    
    depression_keywords = [
        "nu mai pot", "nu mai vreau", "nu are sens", "ce rost", "de ce", "prea mult",
        "obosit", "epuizat", "gol", "singur", "nimeni", "nimic", "mereu la fel",
        "nu se va schimba", "nu pot scăpa", "prins", "blocat", "cufundat", "dark",
        "negru", "viață neagră", "fără speranță", "infinit de rău", "nu vreau să trăiesc"
    ]
    
    sarcasm_keywords = [
        "sigur", "evident", "desigur", "normal", "perfect", "bravo", "minunat",
        "super", "grozav", "wow", "fantastic", "extraordinar", "genial"
    ]
    
    exaggeration_markers = [
        "ATÂT de", "ÎN TOȚI TIMPII", "ÎNTOTDEAUNA", "NICIODATĂ", "CEL MAI", 
        "EXTREM", "IMPOSIBIL", "APOCALIPS", "SFÂRȘIT AL LUMII", "ORICÂND"
    ]
    
    hope_keywords = [
        "poate", "sper", "ar putea", "încercam", "voi", "vrem", "plan", "vis",
        "mai bine", "schimbare", "pas", "încerc", "cred", "speranță"
    ]
    
    for kw in depression_keywords:
        if kw in text_lower:
            markers["depression_markers"].append(kw)
    
    for kw in sarcasm_keywords:
        if kw in text_lower:
            markers["sarcasm_indicators"].append(kw)
    
    for kw in exaggeration_markers:
        if kw in text:
            markers["exaggeration_markers"].append(kw)
    
    for kw in hope_keywords:
        if kw in text_lower:
            markers["hope_markers"].append(kw)
    
    return markers


def detect_sarcasm_and_context(text, last_score=None):
    try:
        text_lower = text.lower()
        sarcasm_score = 0.0
        
        # Markeri de sarcasm
        positive_words = [
            "perfect", "minunat", "grozav", "super", "excelent", "fantastic",
            "wow", "amazing", "best", "love", "incredible", "awesome"
        ]
        
        negative_context_words = [
            "nu", "prost", "rau", "urât", "gal", "oribil", "groaznic",
            "teribil", "horror", "tragic", "disastruu", "catastrofă"
        ]
        
        # Check for positive + negative mix (classic sarcasm pattern)
        has_positive = any(word in text_lower for word in positive_words)
        has_negative = any(word in text_lower for word in negative_context_words)
        
        if has_positive and has_negative:
            sarcasm_score += 0.6
        
        # Check for ALL CAPS (often indicates sarcasm or exaggeration)
        if text != text_lower:
            caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
            if caps_ratio > 0.3:
                sarcasm_score += 0.3
        
        # If last score was high and now saying positive things = likely masking
        if last_score and last_score > 60:
            if has_positive and not has_negative:
                sarcasm_score += 0.4
        
        # Check for quotes or sarcasm indicators
        if '"' in text or "'" in text:
            sarcasm_score += 0.1
        
        # Clamp between 0 and 1
        return min(1.0, max(0.0, sarcasm_score))
        
    except Exception as e:
        print(f"Eroare sarcasm detection: {e}")
        return 0.0


def analyze_emotional_trajectory(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scor_calculat, category FROM analize WHERE chat_id = ? AND scor_calculat IS NOT NULL ORDER BY id ASC",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return {"trend": "INIȚIAL", "pattern": "N/A", "severity": "N/A"}
        
        scores = [r[0] for r in rows]
        recent_avg = sum(scores[-3:]) / len(scores[-3:]) if len(scores) >= 3 else scores[-1]
        first_avg = sum(scores[:3]) / len(scores[:3]) if len(scores) >= 3 else scores[0]
        
        trend = "📈 ESCALADARE" if recent_avg > first_avg + 15 else \
                "📉 ÎMBUNĂTĂȚIRE" if recent_avg < first_avg - 15 else \
                "➡️ STABIL"
        
        volatility = max(scores) - min(scores)
        pattern = "🔄 OSCILANT" if volatility > 30 else \
                  "⬆️ DEGRADARE PROGRESIVĂ" if scores == sorted(scores) else \
                  "⬇️ RECUPERARE PROGRESIVĂ" if scores == sorted(scores, reverse=True) else \
                  "➡️ RELATIV STABIL"
        
        max_score = max(scores)
        severity = "🔴 CRITICĂ" if max_score >= 80 else \
                   "🟠 RIDICATĂ" if max_score >= 55 else \
                   "🟡 MODERATĂ" if max_score >= 30 else \
                   "🟢 UȘOARĂ"
        
        return {
            "trend": trend,
            "pattern": pattern,
            "severity": severity,
            "volatility": round(volatility, 1),
            "recent_avg": round(recent_avg, 1)
        }
    except Exception as e:
        print(f"Eroare analiză traictorie: {e}")
        return {"trend": "N/A", "pattern": "N/A", "severity": "N/A"}


def generate_personalized_insight(chat_id, text_content, ai_data, linguistic_markers):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        # Extrage ultimele 15 mesaje pentru analiză mai profundă
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, category, data FROM analize 
            WHERE chat_id = ? ORDER BY id DESC LIMIT 15
        """, (chat_id,))
        history = cursor.fetchall()
        conn.close()
        
        insights = []
        
        if not history:
            return ["Aceasta este prima ta conversație - încerc să te cunosc mai bine și să înțeleg starea ta prin intermediul mesajelor."]
        
        history.reverse()  # Ordonare cronologică
        scores = [r[2] for r in history if r[2] is not None]
        
        # 🔥 1. TREND ANALYSIS
        if len(scores) >= 4:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:3]) / 3
            delta = recent_avg - older_avg
            
            if delta > 15:
                insights.append(f"📈 **Deteriorare crescândă**: Media scorurilor tale a crescut cu {delta:.0f}% - pare că starea ta se înrăutățește. S-a întâmplat ceva deosebit recent?")
            elif delta < -15:
                insights.append(f"📉 **Recuperare vizibilă**: Starea ta s-a îmbunătățit vizibil față de acum o vreme, cu {abs(delta):.0f}% - chiar dacă poate nu o simți direct. Se observă progrese clare.")
            elif abs(delta) <= 5:
                insights.append("🔄 **Stagnare emoțională**: Scorurile tale rămân la un nivel constant - nu este nici mai rău, dar nici mai bine. Acest platou indică faptul că pattern-ul emoțional persistă.")
        
        # 🎯 2. PATTERN DE TIMP
        if len(history) >= 5:
            high_scores = [i for i, s in enumerate(scores) if s and s > 70]
            low_scores = [i for i, s in enumerate(scores) if s and s < 40]
            
            if high_scores:
                insights.append(f"⏰ **Moment critic**: Starea ta pare să se înrăutățească în special în preajma mesajului #{high_scores[0]+1} din conversație - este posibil să existe anumiți factori declanșatori în acel punct.")
            
            if low_scores:
                insights.append(f"💚 **Moment de respiro**: Există și perioade în care starea ta este mai ușoară (cum a fost la mesajul #{low_scores[0]+1}) - acest lucru arată că suferința nu este permanentă.")
        
        # 🎭 3. SARCASM & MASCARE
        sarcasm_count = sum(1 for h in history if h[3] and "sarcasm" in h[3].lower())
        if sarcasm_count >= 3:
            insights.append(f"😏 **Mecanism defensiv**: Folosești umorul sau sarcasmul defensiv destul de des (de aproximativ {sarcasm_count} ori) pentru a te proteja de vulnerabilitate. Este o strategie valabilă, dar care poate bloca exprimarea reală.")
        
        if ai_data.get("este_mascare_psihica"):
            insights.append("🪄 **Disociere**: Cuvintele folosite par pozitive, dar contextul sau tonul general le contrazic. Îți sugerez să încerci să exprimi ceea ce simți cu adevărat, fără filtre.")
        
        # 💔 4. MARKERS RECURENȚI
        depression_markers = linguistic_markers.get("depression_markers", [])
        if "gol" in depression_markers or "epuizat" in depression_markers:
            insights.append("💔 **Sentimentul de gol**: Cuvântul 'gol' sau 'epuizat' apare repetat în mesajele tale. Aceasta nu este doar o oboseală fizică, ci o epuizare emoțională profundă care necesită atenție.")
        
        if "singur" in depression_markers:
            insights.append("👤 **Sentimentul de izolare**: Termenul 'singur' este un element cheie în exprimarea ta. Izolarea emoțională se face simțită chiar și atunci când ești înconjurat de oameni.")
        
        if "nu mai pot" in depression_markers or "nu mai vreau" in depression_markers:
            insights.append("🚨 **Epuizare existențială**: Această exprimare indică un nivel ridicat de burnout mental și emoțional. Ar fi extrem de util să ceri sprijinul cuiva drag sau al unui specialist.")
        
        # ✨ 5. SPERANȚĂ
        hope_markers = linguistic_markers.get("hope_markers", [])
        if len(hope_markers) >= 2:
            insights.append(f"✨ **Semne de speranță**: Chiar și în momentele dificile, ai folosit termeni plini de speranță precum '{', '.join(hope_markers[:2])}'. Aceasta arată că în interiorul tău există dorința de recuperare.")
        elif len(hope_markers) == 1:
            insights.append(f"🔦 **Un fir de speranță**: Chiar și o singură exprimare legată de speranță ('{hope_markers[0]}') în acest context este o dovadă importantă a forței tale interioare.")
        
        # 📊 6. PROGRESIE
        if len(scores) >= 7:
            primera = scores[0]
            ultima = scores[-1]
            diff = ultima - primera
            
            if diff > 30:
                insights.append(f"📉 **Degradare progresivă**: De la începutul sesiunilor ({primera:.0f}%) și până în prezent ({ultima:.0f}%), se observă o accentuare a dificultăților. Este important să acționezi din timp pentru a te proteja.")
            elif diff < -30:
                insights.append(f"📈 **Evoluție pozitivă**: De la un scor inițial de {primera:.0f}%, ai ajuns în prezent la {ultima:.0f}%. Este o recuperare consistentă, continuă în această direcție!")
            else:
                insights.append(f"🎢 **Fluctuații emoționale**: Scorul tău a evoluat de la {primera:.0f}% la {ultima:.0f}%, indicând oscilații semnificative. Această instabilitate necesită o monitorizare atentă.")
        
        # 🎪 7. EXAGERARE
        exaggeration = linguistic_markers.get("exaggeration_markers", [])
        if len(exaggeration) > 3:
            insights.append(f"🎭 **Intensitate verbală**: Folosești des cuvinte de intensitate maximă pentru a-ți exprima starea. Aceasta poate indica faptul că durerea este atât de mare încât simți nevoia să folosești termeni extremi pentru a fi înțeles.")
        
        # 🌊 8. ISTORIC COMPARATIV
        categories = Counter([h[3] for h in history if h[3]])
        if categories:
            most_common_cat = categories.most_common(1)[0][0]
            insights.append(f"🏷️ **Starea ta predominantă**: În ultima perioadă, starea ta s-a încadrat cel mai frecvent în categoria '{most_common_cat}'.")
        
        return insights[:5]  # Top 5 insights
        
    except Exception as e:
        print(f"Eroare insight personalizat: {e}")
        return ["Momentan nu pot fi generate insight-uri suplimentare. Continuă discuția pentru a acumula date."]


def extract_pattern_analysis(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, category, data FROM analize 
            WHERE chat_id = ? AND scor_calculat IS NOT NULL ORDER BY id ASC LIMIT 25
        """, (chat_id,))
        history = cursor.fetchall()
        conn.close()
        
        if len(history) < 2:
            return {
                "overview": "Conversația a început - încă nu am suficiente date pentru analiza tiparelor.",
                "volatility_interpretation": "N/A",
                "recovery_pattern": "N/A",
                "triggers": "N/A",
                "resilience_signs": "N/A"
            }
        
        analysis = {}
        scores = [r[2] for r in history if r[2] is not None]
        
        # === 1. VOLATILITATE ===
        if scores:
            volatility = max(scores) - min(scores)
            if volatility > 40:
                analysis["volatility_interpretation"] = f"🌊 **Instabilitate accentuată** (variație de {volatility:.0f}pt): Trăirile tale fluctuează dramatic într-un timp scurt, indicând o lipsă de ancore emoționale stabile în prezent."
            elif volatility > 25:
                analysis["volatility_interpretation"] = f"⚡ **Fluctuații moderate** (variație de {volatility:.0f}pt): Emoțiile se schimbă destul de rapid, fiind probabil influențate de factori declanșatori externi."
            else:
                analysis["volatility_interpretation"] = f"📍 **Stare stabilă** (variație de {volatility:.0f}pt): Emoțiile se mențin în limite relativ constante, indicând o stabilitate a trăirilor sau o stare emoțională constantă."
        
        # === 2. TREND ===
        if len(scores) >= 5:
            recent_trend = sum(scores[-3:]) / 3 if len(scores) >= 3 else scores[-1]
            older_trend = sum(scores[:3]) / 3 if len(scores) >= 3 else scores[0]
            delta = recent_trend - older_trend
            
            if delta > 20:
                analysis["trend"] = f"Deteriorare emoțională: scorurile recente indică o stare mai gravă cu {delta:.0f} puncte."
            elif delta < -20:
                analysis["trend"] = f"Îmbunătățire vizibilă: starea ta s-a ameliorat cu {abs(delta):.0f} puncte, indicând un progres real."
            else:
                analysis["trend"] = f"Stagnare emoțională: oscilațiile sunt nesemnificative ({delta:.0f} puncte), indicând menținerea aceleiași stări."
        
        # === 3. MOMENTE DE RECUPERARE ===
        recovery_count = 0
        recovery_moments = []
        for i in range(1, len(scores)):
            if scores[i] < scores[i-1] * 0.8:  # Drop semnificativ (>20%)
                recovery_count += 1
                recovery_moments.append((i, scores[i-1], scores[i]))
        
        if recovery_count >= 3:
            analysis["recovery_pattern"] = f"💪 **Eforturi de redresare**: S-au înregistrat {recovery_count} tentative clare de autoreglare emoțională. Este o dovadă clară că nu renunți la luptă."
        elif recovery_count == 0:
            analysis["recovery_pattern"] = "⚠️ **Fără semne de redresare spontană**: Scorul tău stagnează la un nivel ridicat sau crește constant, indicând o stare de blocaj."
        else:
            analysis["recovery_pattern"] = f"🤔 **Redresare sporadică**: S-au observat doar {recovery_count} momente de ameliorare spontană, indicând un efort încă fragil de echilibrare."
        
        # === 4. PUNCTE DE RUPERE ===
        peak_score = max(scores) if scores else 0
        peak_idx = scores.index(peak_score) if peak_score in scores else -1
        
        if peak_idx >= 0 and peak_idx < len(history):
            peak_text = history[peak_idx][0] or history[peak_idx][1] or "[imagine]"
            peak_category = history[peak_idx][3]
            analysis["triggers"] = f"🚨 **Punct critic**: Scor de {peak_score:.0f}% ({peak_category}). Mesajul asociat: \"{peak_text[:50]}...\" - Acesta este punctul tău de maximă vulnerabilitate."
        
        # === 5. SEMNE DE REZILIENȚĂ ===
        high_scores_with_hope = 0
        for h in history:
            if h[2] and h[2] > 60 and h[0]:  # Scor ridicat = durere, DAR mesajul e lung = efort de comunicare
                if len((h[0] or "")) > 20:
                    high_scores_with_hope += 1
        
        if high_scores_with_hope >= 2:
            analysis["resilience_signs"] = "✨ **Reziliență ridicată**: Chiar și în momentele cele mai dificile, faci efortul de a comunica în detaliu și de a exprima ceea ce simți. Aceasta este o forță interioară prețioasă."
        elif any(s < 40 for s in scores[-3:]):
            analysis["resilience_signs"] = "🔦 **Semne de speranță**: După perioade mai severe, starea ta revine temporar la un nivel de confort. Reziliența ta este activă."
        else:
            analysis["resilience_signs"] = "⚠️ **Reziliență fragilă**: Nu se observă eforturi de redresare. Îți recomandăm să iei măsuri active sau să consulți un specialist."
        
        # === 6. CONSISTENCY SCORE ===
        volatility = max(scores) - min(scores) if scores else 0
        consistency = max(0, min(100, 100 - (volatility / 100 * 100)))
        analysis["consistency_score"] = consistency
        
        return analysis
        
    except Exception as e:
        print(f"Eroare pattern analysis: {e}")
        return {
            "overview": "Eroare în analiza tiparelor. Continuă conversația.",
            "volatility_interpretation": "N/A",
            "recovery_pattern": "N/A",
            "triggers": "N/A",
            "resilience_signs": "N/A"
        }


def get_varied_closing_messages():
    import random
    
    messages_by_type = {
        "validation": [
            "Ceea ce descrii este real. Nu este doar în imaginația ta.",
            "Validez în totalitate ceea ce simți.",
            "Această emoție pe care o simți este pe deplin justificată.",
            "Ceea ce spui are sens și este de înțeles. Suferința ta are o cauză reală."
        ],
        "depth_seeking": [
            "Aș vrea să înțeleg mai bine: ce anume te-a adus în acest punct?",
            "Mă întreb: ce se ascunde, de fapt, în spatele acestor cuvinte?",
            "Simt că sunt mai multe straturi în ceea ce spui și aș vrea să le explorăm împreună.",
            "Sună a ceva mai profund decât cuvintele scrise. Există ceva ce nu vrei sau nu poți să exprimi încă?"
        ],
        "pattern_reflection": [
            "Nu este prima dată când menționezi acest lucru. Observarea acestui tipar este foarte importantă.",
            "Observ că revii mereu la tema asta. De ce crezi?",
            "Acesta pare să fie un element constant în discuția noastră, o cheie pentru a înțelege mai bine situația.",
            "Faptul că repeți acest lucru îmi arată că este o problemă importantă care necesită atenție."
        ],
        "hope_affirmation": [
            "Chiar și în aceste momente grele, reușești să găsești resurse pozitive. Acest lucru este extrem de important.",
            "Faptul că deschizi acest subiect cu mine este o dovadă că undeva, în interior, încă mai ai speranță.",
            "Faptul că ești aici și comunici arată că nu ai renunțat. Există o parte din tine care vrea să fie bine.",
            "Speranța ta nu a dispărut de tot, este doar amorțită acum. Putem încerca să o readucem la viață."
        ],
        "crisis_alert": [
            "Ceea ce descrii indică o suferință extrem de intensă, de nivelul unei urgențe emoționale.",
            "La acest nivel de suferință, este esențial să ceri sprijin. Nu trebuie să treci prin asta singur.",
            "Această stare indică o situație de criză. Te rog, contactează Telefonul Speranței la 0800 801 200 sau sună direct la 112.",
            "Această durere reflectă un nivel ridicat de risc. Te îndemn să cauți sprijin profesional cât mai curând."
        ],
        "resilience_affirmation": [
            "Faptul că reziști și continui să cauți o cale de ieșire, în ciuda persistenței acestei stări, reflectă o putere interioară considerabilă.",
            "Reziliența ta se vede din simplul fapt că alegi să nu îți ascunzi suferința și să vorbești deschis.",
            "Efortul pe care îl depui pentru a te exprima arată o forță interioară extraordinară.",
            "Doar oamenii cu adevărat puternici își permit să fie vulnerabili. Vulnerabilitatea este o formă de curaj."
        ],
        "contextual_exploration": [
            "De cât timp este așa? Când a început?",
            "A fost cândva mai bine? Ce s-a schimbat?",
            "Cine din viața ta mai știe despre această situație?",
            "Ce înseamnă pentru tine această durere? Ce îți este teamă că s-ar întâmpla dacă ea ar dispărea?"
        ],
        "masking_confrontation": [
            "Spui că totul este în regulă, dar mesajele tale transmit altceva. Cum te simți cu adevărat?",
            "Simt o deconectare între ceea ce spui și ceea ce transmiți. Spune-mi ce este real pentru tine acum.",
            "Cuvintele și starea transmisă par să se contrazică. Care este realitatea din spatele lor?",
            "Încerci să maschezi suferința în spatele unor emoticoane pozitive, deși mesajul este unul dureros. Te invit să vorbești liber, fără măști."
        ],
        "sarcasm_processing": [
            "Umor defensiv. Folosești asta pentru a evita vulnerabilitatea?",
            "Sarcasmul tău este un scut inteligent de protecție, dar dincolo de el se simte o durere reală.",
            "Glumești pe seama suferinței, dar durerea rămâne reală. Ce încerci să protejezi prin umor?",
            "Ironia este un mecanism eficient de apărare pentru tine, însă nu vindecă rana din profunzime."
        ],
        "agency_building": [
            "Ce ai putea face pentru tine astăzi? Chiar și un singur gest minor contează.",
            "Dacă ai face o mică schimbare astăzi, care ar fi aceea?",
            "Tu ești cel care poate decide direcția propriei povești. Ce pas simți că ai vrea să faci?",
            "Nu putem schimba trecutul, dar astăzi avem puterea de a alege un pas mic înainte."
        ],
        "professional_recommendation": [
            "Asta depășește conversația. Ai nevoie de terapeut.",
            "Sunt bun la a-ți asculta. Dar tu ai nevoie de cineva cu calificări mai mari.",
            "Îți recomand cu căldură să consulți un psihoterapeut, deoarece depășirea acestei stări necesită sprijin de specialitate.",
            "Suferința ta merită un răspuns din partea unui specialist, nu doar a unui chatbot. Te rog, caută un psiholog cât mai curând."
        ]
    }
    
    return messages_by_type



def get_recent_context(chat_id):
    """Returnează ultimele 3 schimburi (optimizat pentru tokenii Groq)."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback, scor_calculat, category
            FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 3
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "Primul mesaj din sesiune."

        rows.reverse()
        lines = []
        for r in rows:
            user_msg = (r[0] or r[1] or "[imagine]")[:80]  # Trunchiaza la 80 char
            feedback = (r[2] or "")[:60] if r[2] else ""  # Trunchiaza feedback
            if feedback:
                lines.append(f'User: "{user_msg}" → {r[3]}% ({r[4]})')
            else:
                lines.append(f'User: "{user_msg}" → {r[3]}%')
        return "\n".join(lines) if lines else "Primul mesaj."
    except Exception as e:
        print(f"Eroare context: {e}")
        return ""


def get_last_score(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scor_calculat, category FROM analize WHERE chat_id = ? AND scor_calculat IS NOT NULL ORDER BY id DESC LIMIT 1",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return (row[0], row[1]) if row else (None, None)
    except:
        return (None, None)


def get_last_voice_score(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT voice_score FROM voice_analysis WHERE chat_id = ? AND voice_score IS NOT NULL ORDER BY id DESC LIMIT 1",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None


def get_last_face_score(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT depression_score FROM face_analysis WHERE chat_id = ? AND depression_score IS NOT NULL ORDER BY id DESC LIMIT 1",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except:
        return None



def generate_local_voice_feedback(voice_score, voice_analysis, transcript):
    descriptions = voice_analysis.get("descriptions", [])
    
    if voice_score < 30:
        status_vocal = "Vocea este dinamică și stabilă, fără semne de oboseală."
    elif voice_score < 60:
        status_vocal = "Vocea prezintă o ușoară oboseală acustică și monotonie."
    else:
        status_vocal = "Vocea indică o oboseală acustică pronunțată și ton aplatizat."
        
    feedback = f"**Interpretare acustică:** {status_vocal}\n"
    if descriptions:
        feedback += f"**Indicatori:** {', '.join(descriptions)}.\n"
    feedback += f"**Energie:** {voice_analysis.get('energy_score', 0)}% | **Ritm:** {voice_analysis.get('pace_score', 0)}% | **Claritate:** {voice_analysis.get('clarity_score', 0)}% | **Ton:** {voice_analysis.get('tone_score', 0)}%."
    return feedback



# ─── LLM ──────────────────────────────────────────────────────────────────────

def get_chat_details(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(chaturi)")
        columns = [r[1] for r in cursor.fetchall()]
        if "tip_detectie" in columns:
            cursor.execute("SELECT nume_persoana, tip_detectie FROM chaturi WHERE id = ?", (chat_id,))
            row = cursor.fetchone()
            if row:
                return row[0] or "Subiect Anonim", row[1] or "mine"
        else:
            cursor.execute("SELECT nume_persoana FROM chaturi WHERE id = ?", (chat_id,))
            row = cursor.fetchone()
            if row:
                return row[0] or "Subiect Anonim", "mine"
        conn.close()
    except Exception as e:
        print(f"Error fetching chat details: {e}")
    return "Subiect Anonim", "mine"


def get_conversational_history(chat_id, limit=6):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback
            FROM analize WHERE chat_id = ? AND scor_calculat IS NULL ORDER BY id DESC LIMIT ?
        """, (chat_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        rows.reverse()
        for r in rows:
            user_text = r[0] or r[1]
            ai_text = r[2]
            if user_text:
                clean_text = user_text[len("[Mesaj Audio] "):] if user_text.startswith("[Mesaj Audio] ") else user_text
                messages.append({"role": "user", "content": clean_text})
            if ai_text:
                messages.append({"role": "assistant", "content": ai_text})
        return messages
    except Exception as e:
        print(f"Error fetching conversational history: {e}")
        return []


def get_full_chat_history_for_diagnostic(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback
            FROM analize WHERE chat_id = ? ORDER BY id ASC
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "Nicio conversație disponibilă."
            
        history_lines = []
        for r in rows:
            user_text = r[0] or r[1]
            ai_text = r[2]
            if user_text:
                clean_text = user_text[len("[Mesaj Audio] "):] if user_text.startswith("[Mesaj Audio] ") else user_text
                history_lines.append(f"User: {clean_text}")
            if ai_text:
                ai_text_snippet = ai_text[:120] + "..." if len(ai_text) > 120 else ai_text
                history_lines.append(f"AI: {ai_text_snippet}")
        return "\n".join(history_lines)
    except Exception as e:
        print(f"Error fetching full conversational history: {e}")
        return "Eroare context."


def call_llm_conversational(text_content, chat_id, nume_persoana, tip_detectie):
    if tip_detectie == "apropiat":
        system_prompt = (
            f"Ești un consilier emoțional cald, empatic și profesionist. Utilizatorul îți vorbește despre un apropiat numit {nume_persoana} care ar putea avea nevoie de sprijin. Răspunzi în limba română, natural și cald.\n"
            f"REGULI CONVERSAȚIONALE (CRITICAL):\n"
            f"- Răspunde direct și coerent la ceea ce spune utilizatorul. Dacă acesta te salută dar își exprimă și o stare sau o problemă, adresează-te direct acelei stări. NU folosi formule de întâmpinare generice de tipul 'Eu sunt bine, mulțumesc de întrebare' dacă nu ai fost întrebat cum ești.\n"
            f"- Dacă utilizatorul doar te salută, răspunde-i politicos și cald, fără a presupune direct că {nume_persoana} se află într-o criză.\n"
            f"- Fii axat pe înțelegerea situației lui {nume_persoana} (izolare, somn, comportament) prin întrebări firești, puse una câte una pe parcursul dialogului.\n"
            f"- Răspunde cu 1-2 paragrafe de dimensiuni medii. Evită replicile foarte lungi sau reci.\n"
            f"- NU folosi clișee robotice: 'Îmi pare rău să aud asta', 'Sunt aici pentru tine', 'Te înțeleg perfect', 'De asemenea', 'Totodată'.\n"
            f"REGULI DE EXPRIMARE (CRITICAL):\n"
            f"- Scrie corect gramatical, cursiv și elegant în limba română, cu diacritice. Asigură-te că acordul verbal este impecabil și consecvent la persoana a doua singular 'tu' (ex: 'recunoști și admiți', NU amesteca cu pluralul 'admiteți').\n"
            f"- Evită traduceri literale (NU folosi formulări stâlcite precum 'Îți merg bine ziua?')."
        )
    else:
        system_prompt = (
            "Ești un consilier emoțional cald, profund realist, empatic și profesionist. Răspunzi în limba română, natural, fără clișee.\n"
            "REGULI CONVERSAȚIONALE (CRITICAL):\n"
            "- Răspunde direct și coerent la ceea ce spune utilizatorul. Dacă acesta te salută dar își exprimă și o stare sau o problemă (ex: 'salut, mă simt ciudat'), adresează-te direct acelei stări. NU folosi formule de întâmpinare generice de tipul 'Eu sunt bine, mulțumesc pentru întrebare' dacă utilizatorul nu te-a întrebat explicit cum ești.\n"
            "- Dacă utilizatorul doar te salută simplu (ex: 'hey', 'salut'), răspunde-i prietenos, cald și deschis (ex: 'Bună! Sunt gata să te ascult. Cum merge ziua ta?'), fără a presupune că are probleme sau că este trist.\n"
            "- Răspunde cu 1-2 paragrafe de dimensiuni medii. Evită replicile prea lungi, dar și pe cele telegrafice sau reci.\n"
            "- NU folosi niciodată clișee robotice precum: 'Îmi pare rău să aud asta', 'Te înțeleg', 'Sunt aici să te sprijin', 'De asemenea', 'În plus', 'Prin urmare'.\n"
            "REGULI DE EXPRIMARE (CRITICAL):\n"
            "- Scrie corect și elegant în limba română, cu diacritice. Asigură-te că acordul verbal este impecabil și consecvent la persoana a doua singular 'tu' (ex: 'recunoști și admiți', NU amesteca cu persoana a doua plural 'admiteți').\n"
            "- Evită traduceri literale sau greșeli gramaticale (NU folosi formulări stâlcite precum 'Îți merg bine ziua?').\n"
            "- Pune o singură întrebare simplă și firească la final pentru a continua dialogul, fără a fi intruziv de la început."
        )

    history_msgs = get_conversational_history(chat_id, limit=6)
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history_msgs:
        messages.append(msg)
    messages.append({"role": "user", "content": text_content})
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.5,
    }
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        print(f"🔑 Groq conversational status: {response.status_code}")

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return content.strip()
        else:
            print(f"❌ Groq conversational eroare: {response.status_code} - {response.text[:300]}")
            return "Îmi pare rău, a intervenit o eroare de conexiune. Te rog să încerci din nou."
    except Exception as e:
        print(f"❌ Excepție Groq conversational: {e}")
        return "Îmi pare rău, a intervenit o eroare în procesarea răspunsului."


def call_llm_api(text_content, istoric_context, last_score, last_category, linguistic_markers, sarcasm_score, tip_detectie="mine", nume_persoana="Subiect Anonim"):
    """
    Apelează Groq cu prompt ultra-sofisticat și ergonomic care analizează istoria conversației pentru evaluarea stării de spirit.
    """
    subject_info = f"subiectul este utilizatorul însuși" if tip_detectie == "mine" else f"subiectul este o persoană apropiată numită {nume_persoana} (utilizatorul este aparținătorul)"
    
    system_prompt = (
        "Ești un consilier emoțional cald și empatic, expert în analiza stărilor sufletești. Rolul tău este să analizezi întreaga istorie a conversației "
        "dintre utilizator și AI pentru a structura o evaluare a stării de spirit și a identifica indicatori de tristețe, stres și risc. Răspunde în limba română, scriind impecabil gramatical, "
        "natural și cu diacritice. Evită clișeele de traducere automată din engleză sau limbajul rigid AI.\n"
        "REGULI DE GRAMATICĂ ȘI EXPRIMARE DIRECTE (CRITICAL):\n"
        "- NU folosi NICIODATĂ 'să te apărezi' sau 'să se apăreze'. Spune corect: 'să te aperi' / 'să se apere'.\n"
        "- NU folosi NICIODATĂ 'tu înșiși'. Spune corect: 'tu însuți'.\n"
        "- NU folosi traduceri literale de tipul 'îți vor face plouă'. Folosește expresii românești naturale: 'îți vor strica dispoziția', 'îți vor strica planurile' sau 'îți vor pune bețe în roate'.\n"
        "- EVITĂ structurile repetitive ca 'Pare că...' sau 'Se pare că...' la fiecare început de frază. Fă raportul fluid, organic și profesional.\n"
        f"Context subiect: {subject_info}.\n"
        "Analizează semnele de: depresie cronică/ascunsă, tristețe temporară vs profundă, disociere/mascare, sarcasm, umor ca mecanism de adaptare, sau risc de autoaccidentare.\n"
        "Fii extrem de vigilent la exprimări implicite de abandon sau planuri de criză. Fraze precum 'renunț la tot diseară', 'o să termin cu toate în seara asta' sau 'nu o să mă mai trezesc' trebuie clasificate obligatoriu ca 'text_are_plan_iminent': true și 'scor_intensitate_negativa': 9 sau 10.\n"
        "Returnează EXCLUSIV un obiect JSON cu următoarea structură, fără markdown sau text adițional:\n"
        "{\n"
        '  "text_contine_adio": <bool>,\n'
        '  "text_are_plan_iminent": <bool>,\n'
        '  "text_indica_depresie_cronica": <bool>,\n'
        '  "text_indica_depresie_ascunsa": <bool>,\n'
        '  "text_indica_frustrare_stres": <bool>,\n'
        '  "text_are_umor_sau_emoji": <bool>,\n'
        '  "text_are_umor_negru": <bool>,\n'
        '  "text_este_sarcastic": <bool>,\n'
        '  "text_este_pozitiv_sau_bucuros": <bool>,\n'
        '  "text_indica_autoaccidentare_sau_arme": <bool>,\n'
        '  "este_tristete_normala": <bool>,\n'
        '  "este_mascare_psihica": <bool>,\n'
        '  "scor_intensitate_negativa": <0-10 int, unde 0-2=Normal, 3-5=Tristețe/Stres, 6-7=Depresie, 8=Ideație pasivă, 9-10=Plan/Urgență>,\n'
        '  "incertitudine_nivel": <0.0-1.0 float>,\n'
        '  "rationament": "<1-2 fraze scurte despre scor, formulate empatic în română, cu diacritice, respectând regulile de gramatică de mai sus>",\n'
        '  "avertismente_speciale": "<avertisment scurt sau empty>",\n'
        '  "feedback": "<EVALUARE PERSONALIZATĂ ȘI REALISTĂ (2-4 paragrafe scurte, fără clișee AI precum \'Îmi pare rău\', \'Este important de menționat că\' sau limbaj rigid). NU folosi sub nicio formă cuvinte precum \'pacient\', \'doctor\', \'medic\', \'clinic\', \'terapeut\', \'terapie\', \'diagnoză\' sau derivate ale acestora. Dacă tipul de detecție este \'mine\', scrie un mesaj cald, empatic și de sprijin adresat direct utilizatorului (persoana a II-a, \'tu\'), explicându-i blând și pe ocolite ce ai observat din istoric, fără să îl rănești sau să fii brutal de direct. Dacă tipul de detecție este \'apropiat\', fii extrem de direct, franc și detaliat (blunt) pentru aparținător, descriind absolut tot ce ai descoperit în comportamentul și tonul lui ' + nume_persoana + ', explicând clar de ce este așa. Oferă 2-3 recomandări practice adaptate corespunzător. Răspunde în română, cu diacritice.>"\n'
        "}"
    )

    user_prompt = (
        f"Analizează următorul istoric de conversație:\n"
        f"=== ISTORIC CONVERSAȚIE ===\n{istoric_context}\n\n"
        f"Ultimul mesaj primit acum: \"{text_content}\"\n\n"
        f"=== DATE SUPLIMENTARE ===\n"
        f"Scor anterior: {last_score}% ({last_category if last_category else 'N/A'})\n"
        f"Markeri lingvistici text: {linguistic_markers}\n"
        f"Scor sarcasm: {round(sarcasm_score * 100)}%\n"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        print(f"🔑 Groq status: {response.status_code}")

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            parsed = json.loads(content)
            print(f"✅ Groq răspuns: scor={parsed.get('scor_intensitate_negativa')}, rationament={parsed.get('rationament')}")
            return parsed
        else:
            print(f"❌ Groq eroare: {response.status_code} - {response.text[:300]}")
            return None

    except Exception as e:
        print(f"❌ Excepție Groq call_llm_api: {e}")
        return None


def call_llm_voice_diagnostic_api(text_content, voice_features, voice_scores, istoric_context, last_score, last_cat, linguistic_markers, sarcasm_score, tip_detectie="mine", nume_persoana="Subiect Anonim"):
    subject_info = f"subiectul este utilizatorul însuși" if tip_detectie == "mine" else f"subiectul este o persoană apropiată numită {nume_persoana} (utilizatorul este aparținătorul)"
    
    system_prompt = (
        "Ești un consilier emoțional cald și empatic, expert în analiza stărilor sufletești și a parametrilor acustici ai vocii (energie, tempo, pitch, claritate). "
        "Rolul tău este să analizezi întreaga istorie a conversației, transcriptul mesajului vocal și parametrii acustici ai semnalului audio pentru a genera o evaluare a stării de spirit a utilizatorului "
        "și a-i oferi sprijin personalizat sau a informa aparținătorul. Răspunde în limba română, scriind impecabil gramatical, "
        "natural și cu diacritice. Evită clișeele de traducere automată din engleză sau limbajul rigid AI.\n"
        "REGULI DE GRAMATICĂ ȘI EXPRIMARE DIRECTE (CRITICAL):\n"
        "- NU folosi NICIODATĂ 'să te apărezi' sau 'să se apăreze'. Spune corect: 'să te aperi' / 'să se apere'.\n"
        "- NU folosi NICIODATĂ 'tu înșiși'. Spune corect: 'tu însuți'.\n"
        "- NU folosi traduceri literale de tipul 'îți vor face plouă'. Folosește expresii românești naturale: 'îți vor strica dispoziția', 'îți vor strica planurile' sau 'îți vor pune bețe în roate'.\n"
        "- EVITĂ structurile repetitive ca 'Pare că...' sau 'Se pare că...' la fiecare început de frază. Fă raportul fluid, organic și profesional.\n"
        f"Context subiect: {subject_info}.\n"
        "Fii extrem de vigilent la exprimări implicite de abandon sau planuri de criză. Fraze precum 'renunț la tot diseară', 'o să termin cu toate în seara asta' sau 'nu o să mă mai trezesc' trebuie clasificate obligatoriu ca 'text_are_plan_iminent': true și 'scor_intensitate_negativa': 9 sau 10.\n"
        "Returnează EXCLUSIV un obiect JSON cu următoarea structură, fără markdown sau text adițional:\n"
        "{\n"
        '  "text_contine_adio": <bool>,\n'
        '  "text_are_plan_iminent": <bool>,\n'
        '  "text_indica_depresie_cronica": <bool>,\n'
        '  "text_indica_depresie_ascunsa": <bool>,\n'
        '  "text_indica_frustrare_stres": <bool>,\n'
        '  "text_are_umor_sau_emoji": <bool>,\n'
        '  "text_are_umor_negru": <bool>,\n'
        '  "text_este_sarcastic": <bool>,\n'
        '  "text_este_pozitiv_sau_bucuros": <bool>,\n'
        '  "text_indica_autoaccidentare_sau_arme": <bool>,\n'
        '  "este_tristete_normala": <bool>,\n'
        '  "este_mascare_psihica": <bool>,\n'
        '  "scor_intensitate_negativa": <0-10 int, unde 0-2=Normal, 3-5=Tristețe/Stres, 6-7=Depresie, 8=Ideație pasivă, 9-10=Plan/Urgență>,\n'
        '  "incertitudine_nivel": <0.0-1.0 float>,\n'
        '  "rationament": "<1-2 fraze scurte despre scor, formulate empatic în română, cu diacritice, respectând regulile de gramatică de mai sus>",\n'
        '  "avertismente_speciale": "<avertisment scurt sau empty>",\n'
        '  "feedback": "<EVALUARE MULTIMODALĂ PERSONALIZATĂ (2-4 paragrafe scurte, fără clișee AI precum \'Îmi pare rău\', \'Este important de menționat că\' sau limbaj rigid). NU folosi sub nicio formă cuvinte precum \'pacient\', \'doctor\', \'medic\', \'clinic\', \'terapeut\', \'terapie\', \'diagnoză\' sau derivate ale acestora. Dacă toți parametrii acustici indică o stare normală și echilibrată (risc scăzut, energie normală, tempo bun, modulație variată), confirmă-i utilizatorului că vocea lui sună dinamică, expresivă și plină de viață, bucurându-te alături de el și încurajându-l. Dacă parametrii indică oboseală, letargie sau risc ridicat (energie scăzută, tempo lent, modulație plată etc.), iar tipul de detecție este \'mine\', explică-i blând și pe ocolite ce indică acești parametri ai vocii, fără să îl rănești sau să fii brutal de direct. Dacă tipul de detecție este \'apropiat\' și parametrii sunt normali, descrie direct aparținătorului că vocea lui " + nume_persoana + " sună normal, expresiv și dinamic. Dacă în schimb sunt probleme în analiza vocii, descrie-le franc, blunt și detaliat pentru aparținător, explicând ce indică ele (energie scăzută, tempo lent, modulație plată etc.). Oferă 2-3 recomandări practice adaptate corespunzător. Răspunde în română, cu diacritice.>"\n'
        "}"
    )

    rms_energy = voice_features.get("rms_energy", 0.0)
    tempo = voice_features.get("tempo", 110.0)
    zcr = voice_features.get("zero_crossing_rate", 0.0)
    centroid = voice_features.get("spectral_centroid", 2800.0)
    duration = voice_features.get("duration", 0.0)
    
    acoustic_details = (
        f"1. Energie vocală (RMS): {rms_energy:.4f} (Scor risc energie: {voice_scores.get('energy_score', 0)}% - unde 0% înseamnă energie vocală puternică/sănătoasă, iar 100% înseamnă oboseală/letargie severă)\n"
        f"2. Ritmul vorbirii (Tempo): {tempo:.1f} BPM (Scor risc ritm: {voice_scores.get('pace_score', 0)}% - unde 0% înseamnă ritm normal/alert, iar 100% înseamnă vorbire extrem de lentă/retard psihomotor)\n"
        f"3. Claritate vocală (Zero Crossing Rate): {zcr:.4f} (Scor risc claritate: {voice_scores.get('clarity_score', 0)}% - unde 0% înseamnă articulare clară și distinctă, iar 100% înseamnă mormăială/neclaritate)\n"
        f"4. Ton/Pitch vocal mediu (Spectral Centroid): {centroid:.1f} Hz (Scor risc ton: {voice_scores.get('tone_score', 0)}% - unde 0% înseamnă exprimare expresivă și tonalitate variată, iar 100% înseamnă voce plată și monotonă)\n"
        f"5. Durata mesajului: {duration:.2f} secunde."
    )

    user_prompt = (
        f"Analizează următorul istoric de conversație și parametrii acustici ai noului mesaj vocal:\n"
        f"=== ISTORIC CONVERSAȚIE ===\n{istoric_context}\n\n"
        f"Ultimul mesaj rostit (transcris): \"{text_content}\"\n\n"
        f"=== PARAMETRI ACUSTICI AI SEMNALULUI AUDIO ===\n{acoustic_details}\n\n"
        f"=== DATE SUPLIMENTARE TEXT ===\n"
        f"Scor anterior general: {last_score}% ({last_cat if last_cat else 'N/A'})\n"
        f"Markeri lingvistici text: {linguistic_markers}\n"
        f"Scor sarcasm: {round(sarcasm_score * 100)}%\n"
    )

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        print(f"🔑 Groq voice diagnostic status: {response.status_code}")

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            parsed = json.loads(content)
            print(f"✅ Groq voice diagnostic răspuns: scor={parsed.get('scor_intensitate_negativa')}, rationament={parsed.get('rationament')}")
            return parsed
        else:
            print(f"❌ Groq voice diagnostic eroare: {response.status_code} - {response.text[:300]}")
            return None
    except Exception as e:
        print(f"❌ Excepție Groq voice diagnostic: {e}")
        return None


# ─── SCORING ──────────────────────────────────────────────────────────────────

def calculeaza_scor(ai_data, chat_id, text_content=""):
    """
    Calculează scorul final cu logică perfectă pentru 3 zone:
    ZONE 1 (0-30%): Normal/No Stress
    ZONE 2 (30-70%): Mild-Moderate Stress (nuanțat în 4 sub-niveluri)
    ZONE 3 (70-100%): Severe Depression/Crisis (clear escalation)
    """
    ind_adio       = 1 if ai_data.get("text_contine_adio", False) else 0
    ind_iminent    = 1 if ai_data.get("text_are_plan_iminent", False) else 0
    ind_depresie   = 1 if ai_data.get("text_indica_depresie_cronica", False) else 0
    ind_depresie_ascunsa = 1 if ai_data.get("text_indica_depresie_ascunsa", False) else 0
    ind_stres      = 1 if ai_data.get("text_indica_frustrare_stres", False) else 0
    ind_umor       = 1 if ai_data.get("text_are_umor_sau_emoji", False) else 0
    ind_umor_negru = 1 if ai_data.get("text_are_umor_negru", False) else 0
    ind_sarcasm    = 1 if ai_data.get("text_este_sarcastic", False) else 0
    ind_arme       = 1 if ai_data.get("text_indica_autoaccidentare_sau_arme", False) else 0
    ind_pozitiv    = 1 if ai_data.get("text_este_pozitiv_sau_bucuros", False) else 0
    este_normal    = 1 if ai_data.get("este_tristete_normala", False) else 0
    este_mascare   = 1 if ai_data.get("este_mascare_psihica", False) else 0

    # ─── OVERRIDE DE SIGURANȚĂ PENTRU IMPLICITE CRITICE ───
    text_lower = text_content.lower() if text_content else ""
    
    # Normalizare caractere românești (eliminăm diacriticele pentru a acoperi scrierea fără diacritice)
    normalized_text = text_lower
    replacements = {
        'ă': 'a', 'â': 'a', 'î': 'i', 'ș': 's', 'ț': 't',
        'ş': 's', 'ţ': 't'  # acoperă ambele variante de cedilă/virgulă
    }
    for search, replace in replacements.items():
        normalized_text = normalized_text.replace(search, replace)
        
    tipare_critice = [
        ("renunt", "seara asta"),
        ("renunt", "diseara"),
        ("renunt", "tot"),
        ("pun capat", "tot"),
        ("pun capat", "seara asta"),
        ("pun capat", "diseara"),
        ("plec", "definitiv"),
        ("plec", "totdeauna")
    ]
    for cuvant1, cuvant2 in tipare_critice:
        if cuvant1 in normalized_text and cuvant2 in normalized_text:
            print(f"🚨 Override local: Detectat tipar critic implicit ({cuvant1} + {cuvant2})")
            ind_iminent = 1
            break

    intensitate    = ai_data.get("scor_intensitate_negativa", 3)

    # ═══════════════════════════════════════════════════════════════════
    # SCOR DE BAZĂ - 0-100 direct din intensitate LLM (0-10)
    # ═══════════════════════════════════════════════════════════════════
    scor = intensitate * 10.0

    # Override: dacă există orice indicator critic (adio, iminent, arme), forțează scorul în zona 3 (>= 70%)
    if ind_iminent or ind_adio or ind_arme:
        scor = max(scor, 70.0)

    # ═══════════════════════════════════════════════════════════════════
    # ZONE 1: 0-30% (Normal / No Stress / Healthy)
    # ═══════════════════════════════════════════════════════════════════
    
    if (este_normal or ind_pozitiv or intensitate <= 2) and not (ind_depresie or ind_adio or ind_umor_negru or ind_iminent or ind_arme):
        # Clar normal - cap la 25%
        scor = min(scor, 25.0)
        
        if ind_pozitiv and scor > 15.0:
            scor = 10.0  # Clearly positive
        
        if ind_umor and scor > 20.0 and not ind_sarcasm:
            scor = min(scor, 15.0)  # Humor = healthy coping
    
    # ═══════════════════════════════════════════════════════════════════
    # ZONE 2: 30-70% (Mild to Moderate Stress/Anxiety)
    # Sub-zones for precision:
    #   30-40%: Light stress/anxiety
    #   40-55%: Moderate stress/light depression
    #   55-70%: Significant depression / serious anxiety
    # ═══════════════════════════════════════════════════════════════════
    
    elif scor < 70.0:
        # ZONE 2A: Light stress (30-40%)
        if ind_stres and not (ind_depresie or ind_adio) and scor < 35.0:
            scor = max(scor, 32.0)  # Minimum for identified stress
            scor = min(scor, 40.0)  # Cap at 40% for light stress
        
        # ZONE 2B: Moderate stress + light depression (40-55%)
        elif (ind_stres and ind_depresie_ascunsa) or (ind_stres and scor >= 40.0):
            scor = max(scor, 42.0)
            scor = min(scor, 55.0)
            
            # Umor negru = heavier depression, push to 52-55%
            if ind_umor_negru:
                scor = max(scor, 50.0)
        
        # ZONE 2C: Clear but not severe depression (55-70%)
        elif ind_depresie and not ind_adio:
            scor = max(scor, 58.0)
            scor = min(scor, 70.0)
            
            # Umor negru pushes to 65-70%
            if ind_umor_negru:
                scor = max(scor, 65.0)
    
    # ═══════════════════════════════════════════════════════════════════
    # ZONE 3: 70-100% (Severe Depression / Crisis)
    # Sub-zones:
    #   70-80%: Depresie severă (dar fără plan)
    #   80-90%: Ideație suicidală / plan vague
    #   90-100%: Plan iminent / urgență critică
    # ═══════════════════════════════════════════════════════════════════
    
    else:
        # ZONE 3A: Severe depression without ideation (70-80%)
        if ind_depresie and not (ind_adio or ind_iminent):
            scor = max(scor, 70.0)
            scor = min(scor, 79.0)
        
        # ZONE 3B: Passive ideation "wouldn't mind dying" (80-88%)
        elif ind_adio and not ind_iminent:
            scor = max(scor, 80.0)
            scor = min(scor, 85.0)
        
        # ZONE 3C: Vague suicidal plan or serious intent (85-92%)
        elif ind_iminent and not ind_arme:
            scor = max(scor, 85.0)
            scor = min(scor, 90.0)
        
        # ZONE 3D: URGENȚĂ - Plan + Means or Imminence (92-100%)
        elif (ind_iminent and ind_arme) or (ind_adio and ind_arme):
            scor = max(scor, 92.0)
            scor = min(scor, 100.0)

    # ═══════════════════════════════════════════════════════════════════
    # MASCARE PSIHICĂ: Flag, dar NU reduce scor
    # (Handled în indicators - nu modifica scor)
    # ═══════════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════════
    # CARANTINĂ: Dacă anterior era ridicat, nu permite scăderi extremă
    # (Prevents "suddenly I'm fine" masking to drop from 85% to 10%)
    # ═══════════════════════════════════════════════════════════════════
    
    last_score, last_cat = get_last_score(chat_id)
    if last_score and last_score >= 70.0:
        # Apply quarantine only if there is active psychological masking or the current message contains risk signs
        if este_mascare or not ind_pozitiv or ind_depresie or ind_adio or ind_iminent:
            scor = max(scor, last_score - 15.0)
            if scor < last_score - 15.0:
                print(f"⚠️ Carantină: Prevent drop {last_score}% → {scor}%, set to {max(scor, last_score - 15.0)}%")

    scor_final = round(max(0.0, min(100.0, scor)), 1)

    # ═══════════════════════════════════════════════════════════════════
    # TREND ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    
    trend = "STARE INIȚIALĂ"
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scor_calculat FROM analize WHERE chat_id = ? AND scor_calculat IS NOT NULL ORDER BY id DESC LIMIT 5",
            (chat_id,)
        )
        istoric = [r[0] for r in cursor.fetchall() if r[0] is not None]
        conn.close()
        if istoric:
            medie = sum(istoric) / len(istoric)
            delta = scor_final - medie
            if delta > 15:
                trend = f"🚨 ESCALADARE SEVERĂ (+{round(delta, 1)}%)"
            elif delta > 8:
                trend = f"📈 DETERIORARE (+{round(delta, 1)}%)"
            elif delta < -15:
                trend = f"✅ AMELIORARE SEMNIFICATIVĂ (-{round(abs(delta), 1)}%)"
            elif delta < -8:
                trend = f"📉 UȘOARĂ AMELIORARE (-{round(abs(delta), 1)}%)"
            else:
                trend = "➡️ RELATIV STABIL"
    except Exception as e:
        print(f"Eroare trend: {e}")

    # ═══════════════════════════════════════════════════════════════════
    # CATEGORIE CLINICĂ - PERFECT CALIBRATED PER ZONE
    # ═══════════════════════════════════════════════════════════════════
    
    # ZONE 1: Green
    if scor_final < 20:
        category = "🟢 Stare normală - Echilibru emoțional"
    elif scor_final < 30:
        category = "🟢 Stare emoțională optimă"
    
    # ZONE 2: Yellow (mild to moderate)
    elif scor_final < 40:
        category = "🟡 Stres ușor / Stare de tensiune minimă"
    elif scor_final < 50:
        category = "🟡 Stres moderat / Dispoziție ușor deprimată"
    elif scor_final < 60:
        category = "🟠 Depresie moderată / Stres ridicat"
    elif scor_final < 70:
        category = "🟠 Depresie moderat-severă"
    
    # ZONE 3: Red (severe)
    elif scor_final < 80:
        category = "🔴 Depresie severă - Necesită sprijin profesional"
    elif scor_final < 90:
        category = "🔴 Risc ridicat - Ideație pasivă"
    else:
        category = "🔴 Urgență - Plan iminent"

    return {
        "score": scor_final,
        "category": category,
        "trend_analitic": trend,
        "indicators": {
            "is_adio": bool(ind_adio),
            "is_iminent": bool(ind_iminent),
            "is_depresie": bool(ind_depresie),
            "is_stres": bool(ind_stres),
            "is_umor": bool(ind_umor),
            "is_mascare": bool(este_mascare),
            "is_sarcasm": bool(ind_sarcasm)
        }
    }


# ─── ENDPOINTS ────────────────────────────────────────────────────────────────

@app.route("/get-chats", methods=["GET"])
def get_chats():
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nume_persoana, data_creare, tip_detectie FROM chaturi ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"id": r[0], "nume_persoana": r[1], "data_creare": r[2], "tip_detectie": r[3] if len(r) > 3 else "mine"} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/create-chat", methods=["POST"])
def create_chat():
    try:
        data = request.json or {}
        nume = (data.get("nume") or "").strip() or "Subiect Anonim"
        tip_detectie = (data.get("tip_detectie") or "mine").strip()
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chaturi (nume_persoana, data_creare, tip_detectie) VALUES (?, ?, ?)", (nume, acum, tip_detectie))
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({"id": new_id, "nume_persoana": nume, "data_creare": acum, "tip_detectie": tip_detectie}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete-chat/<int:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        # 1. Clean up face analysis files from disk
        try:
            cursor.execute("SELECT image_url FROM face_analysis WHERE chat_id = ?", (chat_id,))
            images = cursor.fetchall()
            for row in images:
                img_url = row[0]
                if img_url and "/uploads/" in img_url:
                    filename = img_url.split("/uploads/")[-1]
                    filepath = os.path.join(UPLOADS_DIR, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"🗑️ Deleted face snapshot file: {filepath}")
                        except Exception as fe:
                            print(f"⚠️ Failed to delete face snapshot file {filepath}: {fe}")
        except Exception as e:
            print(f"⚠️ Error checking face files: {e}")
            
        # 2. Clean up voice analysis files from disk
        try:
            cursor.execute("SELECT audio_url FROM voice_analysis WHERE chat_id = ?", (chat_id,))
            recordings = cursor.fetchall()
            for row in recordings:
                audio_url = row[0]
                if audio_url and "/uploads/" in audio_url:
                    filename = audio_url.split("/uploads/")[-1]
                    filepath = os.path.join(UPLOADS_DIR, filename)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"🗑️ Deleted voice recording file: {filepath}")
                        except Exception as fe:
                            print(f"⚠️ Failed to delete voice recording file {filepath}: {fe}")
        except Exception as e:
            print(f"⚠️ Error checking voice files: {e}")

        # 3. Clean up database records across all tables
        cursor.execute("DELETE FROM voice_analysis WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM face_analysis WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM multimodal_analysis WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM conversation_context WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM analize WHERE chat_id = ?", (chat_id,))
        cursor.execute("DELETE FROM chaturi WHERE id = ?", (chat_id,))
        
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "User and all multimodal data deleted successfully"}), 200
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
            FROM analize 
            WHERE chat_id = ? 
              AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
              AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
            ORDER BY id ASC
        """, (chat_id,))
        rows = cursor.fetchall()
        conn.close()
        history = []
        for r in rows:
            user_text = r[0] or r[1]
            history.append({"sender": "user", "text": user_text, "data": r[10]})
            history.append({
                "sender": "ai", "text": r[4], "score": r[2],
                "category": r[3], "data": r[10],
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
        cursor.execute(
            "SELECT data, scor_calculat, category FROM analize WHERE chat_id = ? AND scor_calculat IS NOT NULL AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]') AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %') ORDER BY id ASC",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"data": r[0], "score": r[1], "category": r[2]} for r in rows]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get-latest-diagnosis/<int:chat_id>", methods=["GET"])
def get_latest_diagnosis(chat_id):
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        # Get latest text diagnosis details
        cursor.execute("""
            SELECT scor_calculat, category, feedback, data,
                   ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor
            FROM analize 
            WHERE chat_id = ? AND scor_calculat IS NOT NULL 
              AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
              AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
            ORDER BY id DESC LIMIT 1
        """, (chat_id,))
        row = cursor.fetchone()
        
        # Get sarcasm / trajectory details from context
        cursor.execute("""
            SELECT emotional_trajectory, sarcasm_detected
            FROM conversation_context 
            WHERE chat_id = ? ORDER BY id DESC LIMIT 1
        """, (chat_id,))
        context_row = cursor.fetchone()
        
        # Get average voice features
        cursor.execute("SELECT AVG(voice_score) FROM voice_analysis WHERE chat_id = ?", (chat_id,))
        voice_avg = cursor.fetchone()[0] or 0
        
        # Get average face features
        cursor.execute("SELECT AVG(depression_score) FROM face_analysis WHERE chat_id = ?", (chat_id,))
        face_avg = cursor.fetchone()[0] or 0
        
        conn.close()
        
        if not row:
            return jsonify({"status": "no_data", "message": "Nu există nicio diagnoză înregistrată pentru această sesiune."}), 200
            
        combined_average = round((row[0] * 0.5 + voice_avg * 0.25 + face_avg * 0.25), 1)
        
        trajectory_val = "⚖️ Stare inițială"
        if context_row and context_row[0]:
            raw_traj = context_row[0]
            if raw_traj.startswith("{") or "trend" in raw_traj:
                try:
                    import ast
                    parsed_traj = ast.literal_eval(raw_traj)
                    trend_str = parsed_traj.get("trend", "N/A")
                    if trend_str == "INIȚIAL":
                        trajectory_val = "⚖️ Stare inițială"
                    else:
                        trajectory_val = trend_str
                except Exception as ex:
                    print(f"Error parsing trajectory dict: {ex}")
                    trajectory_val = raw_traj
            else:
                trajectory_val = raw_traj
                if trajectory_val == "INIȚIAL":
                    trajectory_val = "⚖️ Stare inițială"

        return jsonify({
            "status": "success",
            "score": row[0],
            "category": row[1],
            "feedback": row[2],
            "data": row[3],
            "indicators": {
                "is_adio": bool(row[4]),
                "is_iminent": bool(row[5]),
                "is_depresie": bool(row[6]),
                "is_stres": bool(row[7]),
                "is_umor": bool(row[8]),
                "is_sarcasm": bool(context_row[1]) if context_row else False
            },
            "trajectory": trajectory_val,
            "voice_avg": round(voice_avg, 1),
            "face_avg": round(face_avg, 1),
            "combined_avg": combined_average
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze-text", methods=["POST"])
def analyze_text():
    try:
        chat_id  = request.form.get("chatId")
        raw_text = request.form.get("rawText", "").strip()
        image_file = request.files.get("image")

        if not chat_id:
            return jsonify({"error": "Parametrul chatId este obligatoriu."}), 400

        ocr_text = ""
        if image_file:
            img = Image.open(io.BytesIO(image_file.read()))
            ocr_text = pytesseract.image_to_string(img).strip()

        working_text = raw_text or ocr_text
        if not working_text:
            return jsonify({"error": "Nu s-au detectat date valide."}), 400

        nume_persoana, tip_detectie = get_chat_details(chat_id)
        trigger_diagnosis = request.form.get("trigger_diagnosis", "").strip().lower()

        if trigger_diagnosis != "true":
            # Conversational mode
            conversational_response = call_llm_conversational(working_text, chat_id, nume_persoana, tip_detectie)
            
            # Salvează în baza de date
            acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn = sqlite3.connect(DB_FILE, timeout=10.0)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analize (chat_id, text_manual, text_ocr, scor_calculat, category,
                                     ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data, feedback)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                chat_id,
                raw_text or None, ocr_text or None,
                None, None,
                None, None, None, None, None,
                acum, conversational_response
            ))
            conn.commit()
            conn.close()
            
            return jsonify({
                "score": None,
                "category": None,
                "feedback": conversational_response,
                "indicators": None,
                "personalized_insights": [],
                "pattern_analysis": None,
                "response_variations": {},
                "trend_statistic": "N/A",
                "avertismente_speciale": "",
                "emotional_trajectory": None,
                "sarcasm_detected": False
            }), 200

        # If trigger_diagnosis is "true", run full clinical logic
        # Construiește contextul extins
        istoric_context = get_full_chat_history_for_diagnostic(chat_id)
        last_score, last_cat = get_last_score(chat_id)
        
        # Analiza lingvistică și sarcasm
        linguistic_markers = analyze_linguistic_markers(working_text)
        sarcasm_score = detect_sarcasm_and_context(working_text, last_score)
        emotional_trajectory = analyze_emotional_trajectory(chat_id)

        # Apelează AI-ul cu date enriched
        ai_data = call_llm_api(working_text, istoric_context, last_score, last_cat, linguistic_markers, sarcasm_score, tip_detectie, nume_persoana)

        if not ai_data:
            return jsonify({
                "score": 0,
                "category": "🟢 STARE GENERALĂ NEUTRĂ",
                "feedback": "Momentan nu pot analiza mesajul. Te rog încearcă din nou.",
                "indicators": {
                    "is_adio": False, "is_iminent": False,
                    "is_depresie": False, "is_stres": False, "is_umor": False,
                    "is_mascare": False, "is_sarcasm": False
                },
                "trend_statistic": "N/A"
            }), 200

        rezultat = calculeaza_scor(ai_data, chat_id, working_text)

        # 🎯 GENERARE INSIGHT PERSONALIZAT (NEW!)
        personalized_insights = generate_personalized_insight(chat_id, working_text, ai_data, linguistic_markers)
        
        # 🔍 PATTERN ANALYSIS (NEW!)
        pattern_data = extract_pattern_analysis(chat_id)
        
        # 💬 VARIED CLOSING (NEW!)
        varied_message_templates = get_varied_closing_messages()

        # Salvează în baza de date
        acum = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analize (chat_id, text_manual, text_ocr, scor_calculat, category,
                                 ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor, data, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            chat_id,
            raw_text or None, ocr_text or None,
            rezultat["score"], rezultat["category"],
            1 if rezultat["indicators"]["is_adio"] else 0,
            1 if rezultat["indicators"]["is_iminent"] else 0,
            1 if rezultat["indicators"]["is_depresie"] else 0,
            1 if rezultat["indicators"]["is_stres"] else 0,
            1 if rezultat["indicators"]["is_umor"] else 0,
            acum, ai_data.get("feedback")
        ))
        
        # Salvează context conversat
        cursor.execute("""
            INSERT OR REPLACE INTO conversation_context (chat_id, emotional_trajectory, pattern_markers, linguistic_markers, sarcasm_detected, last_emotional_state)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            chat_id,
            str(emotional_trajectory),
            str(rezultat["indicators"]),
            str(linguistic_markers),
            1 if sarcasm_score > 0.5 else 0,
            rezultat["category"]
        ))
        
        conn.commit()
        conn.close()

        return jsonify({
            "score": rezultat["score"],
            "category": rezultat["category"],
            "feedback": ai_data.get("feedback"),
            "personalized_insights": personalized_insights,  # NEW!
            "pattern_analysis": pattern_data,  # NEW!
            "response_variations": varied_message_templates,  # NEW! - pentru frontend sa varieze
            "indicators": rezultat["indicators"],
            "trend_statistic": rezultat["trend_analitic"],
            "avertismente_speciale": ai_data.get("avertismente_speciale", ""),
            "emotional_trajectory": emotional_trajectory,
            "sarcasm_detected": sarcasm_score > 0.5
        }), 200

    except Exception as e:
        print(f"❌ Eroare procesare: {e}")
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

        cursor.execute(
            "SELECT data, scor_calculat, category, ind_adio, ind_iminent, ind_depresie FROM analize WHERE chat_id = ? ORDER BY id ASC",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        if len(rows) < 2:
            return jsonify({"status": "DATE INSUFICIENTE", "message": "Sunt necesare minim 2 intrări."}), 200

        log_text = "\n".join([
            f"Intrare {i+1} ({r[0]}): Scor={r[1]}%, Categorie={r[2]} [adio={r[3]}, iminent={r[4]}, depresie={r[5]}]"
            for i, r in enumerate(rows)
        ])

        prompt_raport = f"""Analizează cronologia clinică și returnează EXCLUSIV JSON:
Subiect: {p_row[0]}
Date:
{log_text}

{{
    "punct_debut": "când începe degradarea",
    "faza_critica": "perioada de vârf și intensitatea",
    "punct_terminare": "unde se termină sau dacă persistă",
    "prognostic": "evoluție predictivă"
}}"""

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Returnează exclusiv JSON valid."},
                {"role": "user", "content": prompt_raport}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return jsonify(json.loads(response.json()['choices'][0]['message']['content'])), 200
        return jsonify({"error": "Eroare API raport"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get-chat-stats/<int:chat_id>', methods=['GET'])
def get_chat_stats(chat_id):
    period = request.args.get('period', 'all')
    conn = sqlite3.connect(DB_FILE, timeout=10.0)
    c = conn.cursor()

    query = """
        SELECT scor_calculat, category, feedback, data,
               ind_adio, ind_iminent, ind_depresie, ind_stres, ind_umor
        FROM analize WHERE chat_id = ?
          AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
          AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
    """
    params = [chat_id]
    if period == 'week':
        query += " AND data >= datetime('now', '-7 days')"
    elif period == 'month':
        query += " AND data >= datetime('now', '-30 days')"
    query += " ORDER BY data ASC"

    c.execute(query, params)
    rows = c.fetchall()
    c.execute("SELECT nume_persoana FROM chaturi WHERE id = ?", (chat_id,))
    chat = c.fetchone()

    if not rows:
        conn.close()
        return jsonify({
            'nume_persoana': chat[0] if chat else 'Unknown',
            'scor_mediu': 0, 'total_mesaje': 0, 'total_analize': 0,
            'mesaje_critice': 0, 'categorie_principala': 'N/A',
            'categorie_procent': 0, 'trend': 0,
            'prima_analiza': 'N/A', 'ultima_analiza': 'N/A',
            'categorii': {}, 'top_indicatori': [], 'mesaje_critice_lista': []
        })

    scores     = [r[0] for r in rows if r[0] is not None]
    categories = [r[1] for r in rows if r[1] is not None]
    messages   = [r[2] for r in rows]
    dates      = [r[3] for r in rows]

    indicators_list = [
        {'is_adio': bool(r[4]), 'is_iminent': bool(r[5]),
         'is_depresie': bool(r[6]), 'is_stres': bool(r[7]), 'is_umor': bool(r[8])}
        for r in rows
    ]

    scor_mediu = round(sum(scores) / len(scores), 1) if scores else 0
    total_analize = len(rows)
    mesaje_critice = sum(1 for s in scores if s >= 80)

    categorie_counts = Counter(categories)
    categorie_principala = categorie_counts.most_common(1)[0][0] if categorie_counts else "N/A"
    categorie_procent = round((categorie_counts.get(categorie_principala, 0) / len(categories)) * 100) if categories else 0

    trend = 0
    if len(scores) >= 4:
        trend = round(sum(scores[-2:]) / 2 - sum(scores[:2]) / 2, 1)

    indicatori_count = Counter()
    for ind in indicators_list:
        for key, val in ind.items():
            if val:
                indicatori_count[key.replace('is_', '').capitalize()] += 1

    mesaje_critice_lista = [
        {'score': scores[i], 'text': (messages[i] or "")[:150], 'data': dates[i].split(' ')[0]}
        for i in range(len(scores)) if scores[i] >= 80
    ]

    conn.close()
    return jsonify({
        'nume_persoana': chat[0] if chat else 'Unknown',
        'scor_mediu': scor_mediu,
        'total_mesaje': total_analize,
        'total_analize': total_analize,
        'mesaje_critice': mesaje_critice,
        'categorie_principala': categorie_principala,
        'categorie_procent': categorie_procent,
        'trend': trend,
        'prima_analiza': dates[0].split(' ')[0] if dates else 'N/A',
        'ultima_analiza': dates[-1].split(' ')[0] if dates else 'N/A',
        'categorii': dict(categorie_counts),
        'top_indicatori': [{'nume': n, 'count': c} for n, c in indicatori_count.most_common(5)],
        'mesaje_critice_lista': mesaje_critice_lista[:5]
    })


@app.route("/emotional-trajectory/<int:chat_id>", methods=["GET"])
def get_emotional_trajectory(chat_id):
    """Returnează analiza traiectoriei emoționale complete pentru un chat."""
    try:
        trajectory = analyze_emotional_trajectory(chat_id)
        
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            """SELECT scor_calculat, category, data FROM analize 
               WHERE chat_id = ? AND scor_calculat IS NOT NULL
                 AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
                 AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
               ORDER BY id ASC""",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return jsonify({"error": "Nu există date pentru acest chat"}), 404
        
        scores = [r[0] for r in rows]
        return jsonify({
            "chat_id": chat_id,
            "trajectory_analysis": trajectory,
            "scores_history": scores,
            "min_score": min(scores),
            "max_score": max(scores),
            "avg_score": round(sum(scores) / len(scores), 1),
            "total_messages": len(scores),
            "dates": [r[2] for r in rows]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/advanced-insights/<int:chat_id>", methods=["GET"])
def get_advanced_insights(chat_id):
    """Returnează insights avansate despre pattern-uri, sarcasm, mascare psihică și risc."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT emotional_trajectory, pattern_markers, linguistic_markers, sarcasm_detected, last_emotional_state
            FROM conversation_context WHERE chat_id = ? ORDER BY id DESC LIMIT 1
        """, (chat_id,))
        context_data = cursor.fetchone()
        
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, feedback FROM analize 
            WHERE chat_id = ?
              AND text_manual NOT IN ('[Analiză Generală Multimodală]', '[Analiză Facială]')
              AND (text_manual IS NULL OR text_manual NOT LIKE '[Mesaj Audio] %')
            ORDER BY id DESC LIMIT 5
        """, (chat_id,))
        recent_messages = cursor.fetchall()
        
        cursor.execute(
            "SELECT nume_persoana FROM chaturi WHERE id = ?",
            (chat_id,)
        )
        chat_name = cursor.fetchone()
        conn.close()
        
        if not context_data:
            return jsonify({"error": "Nu există context suficient pentru analiza avansată"}), 404
        
        linguistic_info = context_data[2] if context_data else "{}"
        
        trajectory_val = "⚖️ Stare inițială"
        if context_data and context_data[0]:
            raw_traj = context_data[0]
            if raw_traj.startswith("{") or "trend" in raw_traj:
                try:
                    import ast
                    parsed_traj = ast.literal_eval(raw_traj)
                    trend_str = parsed_traj.get("trend", "N/A")
                    if trend_str == "INIȚIAL":
                        trajectory_val = "⚖️ Stare inițială"
                    else:
                        pattern_str = parsed_traj.get("pattern", "N/A")
                        if pattern_str != "N/A" and pattern_str != "N/A":
                            trajectory_val = f"{trend_str} (Tipar: {pattern_str})"
                        else:
                            trajectory_val = trend_str
                except Exception as ex:
                    print(f"Error parsing trajectory dict: {ex}")
                    trajectory_val = raw_traj
            else:
                trajectory_val = raw_traj
                if trajectory_val == "INIȚIAL":
                    trajectory_val = "⚖️ Stare inițială"

        return jsonify({
            "chat_id": chat_id,
            "nume_persoana": chat_name[0] if chat_name else "Unknown",
            "emotional_trajectory": trajectory_val,
            "pattern_indicators": context_data[1] if context_data else "{}",
            "linguistic_markers": linguistic_info,
            "sarcasm_detected": bool(context_data[3]) if context_data else False,
            "last_emotional_state": context_data[4] if context_data else "N/A",
            "recent_messages": [
                {
                    "text": (m[0] or m[1] or "[imagine]")[:200],
                    "score": m[2],
                    "feedback": m[3]
                }
                for m in recent_messages
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/analyze-voice", methods=["POST"])
def analyze_voice():
    """
    Analyze audio input using Groq Whisper + voice feature extraction
    
    Request body:
    {
        "audio": "base64_encoded_audio_data",
        "chat_id": "optional_chat_id",
        "language": "ro" (default: Romanian),
        "trigger_diagnosis": "true/false"
    }
    """
    if not VOICE_ENABLED:
        return jsonify({"error": "Voice module not enabled"}), 500
    
    try:
        data = request.json or {}
        audio_base64 = data.get("audio", "")
        chat_id = data.get("chat_id")
        language = data.get("language", "auto")
        trigger_diagnosis = str(data.get("trigger_diagnosis", "")).strip().lower()
        
        if not audio_base64:
            return jsonify({"error": "No audio data provided"}), 400
        
        # Decode base64 audio
        try:
            audio_binary = base64.b64decode(audio_base64)
        except Exception as e:
            return jsonify({"error": f"Invalid base64 audio: {str(e)}"}), 400
        
        print("🎤 Processing voice input...")
        
        # Process voice (transcribe + extract features)
        voice_result = process_voice_input(audio_binary, language)
        
        if voice_result.get("status") != "success":
            return jsonify({
                "status": "error",
                "error": voice_result.get("error", "Voice processing failed")
            }), 500
        
        # Get transcript
        transcript = voice_result.get("transcript", "")
        
        # Get voice analysis
        voice_analysis = voice_result.get("analysis", {})
        acoustic_score = voice_analysis.get("overall_voice_indicator", 0)
        
        text_analysis = None
        overall_voice_score = acoustic_score
        
        if transcript and chat_id:
            if trigger_diagnosis == "true":
                # Clinical voice diagnosis - Call Llama to perform semantic and acoustic integrated check
                print("🧠 Calling Groq LLM voice diagnostic API...")
                istoric_context = get_recent_context(chat_id)
                last_score, last_cat = get_last_score(chat_id)
                last_score = last_score if last_score is not None else 0
                
                linguistic_markers = analyze_linguistic_markers(transcript)
                sarcasm_score = detect_sarcasm_and_context(transcript, last_score)
                
                # Fetch chat settings for personalized context
                tip_detectie = "mine"
                nume_persoana = "Subiect Anonim"
                try:
                    conn = sqlite3.connect(DB_FILE, timeout=10.0)
                    cursor = conn.cursor()
                    cursor.execute("SELECT nume_persoana, tip_detectie FROM chaturi WHERE id = ?", (chat_id,))
                    row = cursor.fetchone()
                    if row:
                        nume_persoana = row[0]
                        tip_detectie = row[1] if row[1] else "mine"
                    conn.close()
                except Exception as e:
                    print(f"⚠️ Error reading chat settings for voice: {e}")
                
                llm_result = call_llm_voice_diagnostic_api(
                    text_content=transcript,
                    voice_features=voice_result.get("features", {}),
                    voice_scores=voice_analysis,
                    istoric_context=istoric_context,
                    last_score=last_score,
                    last_cat=last_cat,
                    linguistic_markers=linguistic_markers,
                    sarcasm_score=sarcasm_score,
                    tip_detectie=tip_detectie,
                    nume_persoana=nume_persoana
                )
                
                text_score = 0
                feedback_val = ""
                category_val = ""
                indicators_val = {}
                
                if llm_result:
                    text_score_dict = calculeaza_scor(llm_result, chat_id, transcript)
                    text_score = text_score_dict.get("score", 0)
                    feedback_val = llm_result.get("feedback", "")
                    
                    # Blend the acoustic score and semantic text score
                    # - If content is critical (text_score >= 80%), content overrides acoustics.
                    # - If content is moderate (text_score >= 50%), blend weighted (60% text, 40% acoustic).
                    # - Otherwise, use a balanced blend.
                    if text_score >= 80:
                        overall_voice_score = max(acoustic_score, text_score)
                    elif text_score >= 50:
                        overall_voice_score = int(acoustic_score * 0.40 + text_score * 0.60)
                    else:
                        overall_voice_score = int(acoustic_score * 0.70 + text_score * 0.30)
                        
                    # Apply Voice Quarantine if last voice score was high (>= 70%)
                    last_voice_score = get_last_voice_score(chat_id)
                    if last_voice_score and last_voice_score >= 70.0:
                        overall_voice_score = max(overall_voice_score, last_voice_score - 15.0)
                        print(f"⚠️ Voice Quarantine: Prevent drop {last_voice_score}% → {overall_voice_score}%")
                            
                    # Map the overall score to clinical categories
                    if overall_voice_score < 20:
                        category_val = "🟢 Stare normală - Echilibru acustic"
                    elif overall_voice_score < 30:
                        category_val = "🟢 Stare vocală optimă"
                    elif overall_voice_score < 40:
                        category_val = "🟡 Fatigabilitate acustică ușoară"
                    elif overall_voice_score < 50:
                        category_val = "🟡 Tensiune vocală moderată / Letargie minimă"
                    elif overall_voice_score < 60:
                        category_val = "orange Depresie vocală moderată"
                    elif overall_voice_score < 70:
                        category_val = "orange Depresie vocală moderat-severă"
                    else:
                        category_val = "🔴 Depresie vocală severă - Risc acustic critic"
                        
                    indicators_val = {
                        "is_adio": llm_result.get("text_contine_adio", False),
                        "is_iminent": llm_result.get("text_are_plan_iminent", False),
                        "is_depresie": llm_result.get("text_indica_depresie_cronica", False) or overall_voice_score >= 40,
                        "is_stres": llm_result.get("text_indica_frustrare_stres", False) or (overall_voice_score >= 30 and overall_voice_score < 50),
                        "is_umor": llm_result.get("text_are_umor_sau_emoji", False),
                        "is_mascare": llm_result.get("este_mascare_psihica", False),
                        "is_sarcasm": llm_result.get("text_este_sarcastic", False)
                    }
                else:
                    # Apply Voice Quarantine if last voice score was high (>= 70%)
                    last_voice_score = get_last_voice_score(chat_id)
                    if last_voice_score and last_voice_score >= 70.0:
                        overall_voice_score = max(overall_voice_score, last_voice_score - 15.0)
                        print(f"⚠️ Voice Quarantine (LLM Fail): Prevent drop {last_voice_score}% → {overall_voice_score}%")
                        
                    feedback_val = generate_local_voice_feedback(overall_voice_score, voice_analysis, transcript)
                    if overall_voice_score < 20:
                        category_val = "🟢 Stare normală - Echilibru acustic"
                    elif overall_voice_score < 30:
                        category_val = "🟢 Stare vocală optimă"
                    elif overall_voice_score < 40:
                        category_val = "🟡 Fatigabilitate acustică ușoară"
                    elif overall_voice_score < 50:
                        category_val = "🟡 Tensiune vocală moderată / Letargie minimă"
                    elif overall_voice_score < 60:
                        category_val = "orange Depresie vocală moderată"
                    elif overall_voice_score < 70:
                        category_val = "orange Depresie vocală moderat-severă"
                    else:
                        category_val = "🔴 Depresie vocală severă - Risc acustic critic"
                        
                    indicators_val = {
                        "is_adio": False,
                        "is_iminent": False,
                        "is_depresie": overall_voice_score >= 40,
                        "is_stres": overall_voice_score >= 30 and overall_voice_score < 50,
                        "is_umor": False,
                        "is_mascare": False,
                        "is_sarcasm": False
                    }
                
                text_analysis = {
                    "score": overall_voice_score,
                    "category": category_val,
                    "feedback": feedback_val,
                    "indicators": indicators_val
                }
            else:
                # Conversational mode - return acoustic score immediately without LLM calls
                text_analysis = {
                    "score": None,
                    "category": None,
                    "feedback": None,
                    "indicators": None
                }
        
        # Update voice analysis object with the combined score
        voice_analysis["overall_voice_indicator"] = overall_voice_score
        
        # Save audio file persistently
        audio_url = save_base64_file(audio_base64, f"voice_{chat_id}", "wav")
 
        # Save voice analysis to database (voice_analysis table only, NO insert into analize table)
        if chat_id:
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO voice_analysis
                    (chat_id, transcript, audio_url, voice_score, energy_score, pace_score, clarity_score, tone_score, duration, features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    transcript,
                    audio_url,
                    overall_voice_score,
                    voice_analysis.get("energy_score", 0),
                    voice_analysis.get("pace_score", 0),
                    voice_analysis.get("clarity_score", 0),
                    voice_analysis.get("tone_score", 0),
                    voice_result.get("features", {}).get("duration", 0.0),
                    json.dumps(voice_result.get("features", {}))
                ))
                
                conn.commit()
                conn.close()
                print("✅ Voice analysis saved to database successfully (without mirroring to analize table)")
            except Exception as db_err:
                print(f"❌ Failed to save voice analysis to DB: {db_err}")
        
        return jsonify({
            "status": "success",
            "transcript": transcript,
            "voice_analysis": {
                "overall_voice_indicator": overall_voice_score,
                "energy_score": voice_analysis.get("energy_score", 0),
                "pace_score": voice_analysis.get("pace_score", 0),
                "clarity_score": voice_analysis.get("clarity_score", 0),
                "tone_score": voice_analysis.get("tone_score", 0),
                "descriptions": voice_analysis.get("descriptions", []),
                "features": voice_result.get("features", {})
            },
            "text_analysis": text_analysis,
            "combined_analysis": {
                "voice_depression_indicator": overall_voice_score,
                "text_depression_score": text_analysis.get("score") if text_analysis else None,
                "note": "Voice analysis focuses on acoustic voice quality indicator."
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Voice analysis error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


def analyze_image_context(image_base64, tip_detectie="mine", nume_persoana="Subiect Anonim"):
    """
    Analyzes the visual context of the face image using Groq Llama-3.2 Vision.
    Detects severe risks like weapons, self-harm, gun to head, crying, etc.,
    and classifies facial expressions into the 7 primary emotions.
    """
    import os
    from datetime import datetime
    log_path = os.path.join(os.path.dirname(__file__), "debug_vision_log.txt")
    
    try:
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            lf.write(f"Image length: {len(image_base64) if image_base64 else 0}\n")
            lf.write(f"API Key exists: {bool(GROQ_API_KEY)}\n")
    except Exception as log_err:
        print(f"⚠️ Failed to write initial log: {log_err}")
        
    if not image_base64 or not GROQ_API_KEY:
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write("Error: image_base64 or GROQ_API_KEY is missing\n")
        except:
            pass
        return None
        
    try:
        # Prepare base64 image data URL
        if "," in image_base64:
            image_url = image_base64
        else:
            image_url = f"data:image/jpeg;base64,{image_base64}"
            
        prompt_text = f"""Analyze this image for emotional state and safety assessment. 
Specifically detect danger, self-harm cues, weapons (such as a gun or weapon near a person/head), or a rope/noose/ligature around the neck.
Also classify the person's facial expression into 7 primary emotions (neutral, happy, sad, angry, fearful, disgusted, surprised) as probabilities/scores between 0.0 and 1.0 that sum to approximately 1.0. 
Pay close attention to micro-expressions, muscle tension, eyes (squinted/closed/wide), eyebrows (raised/furrowed/tense), and mouth shape. Note that squeezed or closed eyes combined with tense eyebrows or mouth indicate distress, sadness, pain, or disgust, NOT a neutral state.
Return EXCLUSIVELY a JSON object with this exact schema (no markdown, no other text):
{{
  "has_weapons": <bool>,
  "has_self_harm_intent": <bool>,
  "gun_to_head_detected": <bool>,
  "rope_around_neck_detected": <bool>,
  "crying_or_tears_detected": <bool>,
  "visible_injuries": <bool>,
  "emotional_context": "<brief description, e.g. normal, distress, despair, danger>",
  "context_risk_multiplier": <float between 1.0 and 5.0, where 5.0 is extreme danger, 2.5 is high distress, 1.0 is normal>,
  "emotions": {{
    "neutral": <float between 0.0 and 1.0>,
    "happy": <float between 0.0 and 1.0>,
    "sad": <float between 0.0 and 1.0>,
    "angry": <float between 0.0 and 1.0>,
    "fearful": <float between 0.0 and 1.0>,
    "disgusted": <float between 0.0 and 1.0>,
    "surprised": <float between 0.0 and 1.0>
  }},
  "dominant_emotion": "<one of: neutral, happy, sad, angry, fearful, disgusted, surprised>",
  "confidence": <float between 0.0 and 1.0>,
  "description": "<brief description in Romanian. DO NOT use words like 'pacient', 'doctor', 'medic', 'clinic', 'terapeut', 'terapie', 'diagnoză' or derivatives. Context settings: tip_detectie={tip_detectie}, name={nume_persoana}. If tip_detectie is 'mine', address the user directly (using 'tu'/second person) warmly, gently, and supportively, telling them what expressions you notice on their face without being clinical or brutally direct. If tip_detectie is 'apropiat', be extremely blunt, direct, and detailed (third person) to the guardian, describing exactly what you found on the face of {nume_persoana}, maximum 2 sentences, NO emojis>"
}}"""

        payload = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(f"Groq Response Status: {response.status_code}\n")
        except:
            pass
            
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            try:
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(f"Raw Content: {content}\n")
            except:
                pass
            try:
                parsed = json.loads(content)
                print(f"👁️ Groq Vision Response: {parsed}")
                
                # Check for "silent refusal" in JSON content
                refusal_keywords = [
                    "cannot assist", "safety", "policy", "refuse", "violation", "restricted", "dangerous", "unable to", "unfortunate",
                    "nu pot", "imi pare rau", "îmi pare rău", "reguli", "politic", "siguranț", "sigurant", "refuz", "nepermis", "blocat", "restrict"
                ]
                
                is_refusal = False
                
                # Check for explicit refusal/error keys
                for k, v in parsed.items():
                    if k.lower() in ["error", "refusal", "message", "decline", "reason"]:
                        val_str = str(v).lower()
                        if any(word in val_str for word in refusal_keywords) or any(w in val_str for w in ["self-harm", "harm", "weapon", "violence", "armă", "arma"]):
                            is_refusal = True
                
                # Check if expected safety keys are missing
                expected_keys = {"has_weapons", "has_self_harm_intent", "gun_to_head_detected", "rope_around_neck_detected"}
                missing_keys = expected_keys - set(parsed.keys())
                if missing_keys:
                    # If keys are missing, and any value in the JSON contains refusal keywords or safety terms, it's a refusal
                    for v in parsed.values():
                        val_str = str(v).lower()
                        if any(word in val_str for word in refusal_keywords) or any(w in val_str for w in ["self-harm", "harm", "weapon", "violence", "armă", "arma"]):
                            is_refusal = True
                            break
                
                # If there are refusal indications in the JSON content, and the safety flags are set to False/missing,
                # it's a silent refusal. We override to true.
                if is_refusal and not (parsed.get("gun_to_head_detected") or parsed.get("rope_around_neck_detected") or parsed.get("has_self_harm_intent") or parsed.get("has_weapons")):
                    print("🚨 Detected safety refusal keywords in parsed JSON content! Overriding to critical risk.")
                    try:
                        with open(log_path, "a", encoding="utf-8") as lf:
                            lf.write("🚨 Silent refusal detected in JSON content! Overriding to critical risk.\n")
                    except:
                        pass
                    parsed["gun_to_head_detected"] = True
                    parsed["rope_around_neck_detected"] = True
                    parsed["has_weapons"] = True
                    parsed["has_self_harm_intent"] = True
                    parsed["context_risk_multiplier"] = 5.0
                    parsed["emotions"] = {
                        "neutral": 0.0,
                        "happy": 0.0,
                        "sad": 1.0,
                        "angry": 0.0,
                        "fearful": 0.0,
                        "disgusted": 0.0,
                        "surprised": 0.0
                    }
                    parsed["dominant_emotion"] = "sad"
                    parsed["confidence"] = 1.0
                    parsed["description"] = "Analiză restricționată de filtrele de siguranță."
                
                return parsed
            except Exception as json_err:
                print(f"⚠️ JSON load failed on Groq Vision content: {json_err}. Content was: {content}")
                try:
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write(f"JSON load failed: {json_err}\n")
                except:
                    pass
                content_lower = content.lower()
                refusal_keywords = [
                    "cannot assist", "safety", "policy", "self-harm", "harm", "weapon", "violence", 
                    "refuse", "violation", "restricted", "dangerous", "unable to", "unfortunate",
                    "nu pot", "imi pare rau", "îmi pare rău", "reguli", "politic", "siguranț", 
                    "sigurant", "armă", "arma", "auto-vătămare", "autovatamare", "violenț", 
                    "violenta", "asista", "refuz", "nepermis", "blocat", "restrict"
                ]
                if any(word in content_lower for word in refusal_keywords):
                    print("🚨 Caught safety refusal text in 200 OK. Escalating to 100% risk.")
                    try:
                        with open(log_path, "a", encoding="utf-8") as lf:
                            lf.write("🚨 Caught safety refusal text in 200 OK! Overriding to critical risk.\n")
                    except:
                        pass
                    return {
                        "has_weapons": True,
                        "has_self_harm_intent": True,
                        "gun_to_head_detected": True,
                        "rope_around_neck_detected": True,
                        "crying_or_tears_detected": False,
                        "visible_injuries": False,
                        "emotional_context": "safety refusal - potential self-harm/danger",
                        "context_risk_multiplier": 5.0,
                        "emotions": {
                            "neutral": 0.0,
                            "happy": 0.0,
                            "sad": 1.0,
                            "angry": 0.0,
                            "fearful": 0.0,
                            "disgusted": 0.0,
                            "surprised": 0.0
                        },
                        "dominant_emotion": "sad",
                        "confidence": 1.0,
                        "description": "Analiză restricționată de filtrele de siguranță."
                    }
                return None
        else:
            error_text = response.text
            print(f"❌ Groq Vision Error: {response.status_code} - {error_text[:300]}")
            try:
                with open(log_path, "a", encoding="utf-8") as lf:
                    lf.write(f"Error Body: {error_text}\n")
            except:
                pass
            error_lower = error_text.lower()
            if any(word in error_lower for word in ["safety", "policy", "harm", "violation", "moderation", "refus", "dangerous"]):
                print("🚨 Groq Vision request blocked by safety/moderation filters. Treating as CRITICAL danger!")
                try:
                    with open(log_path, "a", encoding="utf-8") as lf:
                        lf.write("🚨 Blocked by safety filters (400)! Overriding to critical risk.\n")
                except:
                    pass
                return {
                    "has_weapons": True,
                    "has_self_harm_intent": True,
                    "gun_to_head_detected": True,
                    "rope_around_neck_detected": True,
                    "crying_or_tears_detected": False,
                    "visible_injuries": False,
                    "emotional_context": "blocked by safety filters",
                    "context_risk_multiplier": 5.0,
                    "emotions": {
                        "neutral": 0.0,
                        "happy": 0.0,
                        "sad": 1.0,
                        "angry": 0.0,
                        "fearful": 0.0,
                        "disgusted": 0.0,
                        "surprised": 0.0
                    },
                    "dominant_emotion": "sad",
                    "confidence": 1.0,
                    "description": "Imagine blocată din motive de siguranță."
                }
            return None
    except Exception as e:
        print(f"❌ Exception in analyze_image_context: {e}")
        try:
            with open(log_path, "a", encoding="utf-8") as lf:
                lf.write(f"Exception: {e}\n")
        except:
            pass
        return None


# ─── FACE ANALYSIS ENDPOINTS ──────────────────────────────────────────────────

@app.route("/analyze-face", methods=["POST"])
def analyze_face():
    """
    Analyze face image using Face-API.js detection results
    
    Request body:
    {
        "face_detection": {
            "expressions": { emotion scores from Face-API },
            "detection": { confidence and box },
            "landmarks": { 68 face landmarks (optional) }
        },
        "chat_id": "optional_chat_id",
        "image": "base64_encoded_image_data"
    }
    """
    
    if not FACE_ENABLED:
        return jsonify({"error": "Face module not enabled"}), 500
    
    try:
        data = request.json or {}
        face_detection = data.get("face_detection")
        chat_id = data.get("chat_id")
        image_base64 = data.get("image")
        trigger_diagnosis = str(data.get("trigger_diagnosis", "")).strip().lower()
        
        if not face_detection and not image_base64:
            return jsonify({"error": "No face detection data or image provided"}), 400
        
        print("😊 Processing face analysis...")
        
        # Initialize default indicators and features
        depression_indicators = {
            "sadness_indicator": 0,
            "anxiety_indicator": 0,
            "irritability_indicator": 0,
            "anhedonia_indicator": 0,
            "dissociation_indicator": 0,
            "overall_face_depression_score": 0
        }
        facial_features = {
            "facial_expression": "unknown",
            "expression_confidence": 0.0,
            "detection_quality": "none",
            "notes": []
        }
        face_depression_score = 0
        dominant_emotion = "unknown"
        emotions = {}
        confidence = 0.0
        face_result = None
        
        # Process face detection if it was successfully performed locally
        if face_detection:
            face_result = process_face_input(face_detection)
            if face_result.get("status") == "success":
                depression_indicators = face_result.get("depression_indicators", {})
                facial_features = face_result.get("facial_features", {})
                face_depression_score = depression_indicators.get("overall_face_depression_score", 0)
                
                face_processed = face_result.get("face_processed", {})
                dominant_emotion = face_processed.get("dominant_emotion", "neutral")
                emotions = face_processed.get("emotions", {})
                confidence = face_processed.get("confidence", 0.0)
            else:
                facial_features["notes"].append("⚠️ Local face expression processing failed.")
        else:
            facial_features["notes"].append("⚠️ Detectorul facial local nu a putut identifica trăsături faciale.")
        
        # Decode base64 image data and save file persistently
        image_url = save_base64_file(image_base64, f"face_{chat_id}", "jpg") if image_base64 else "https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=256&auto=format&fit=crop"

        # Fetch chat settings for personalized context
        tip_detectie = "mine"
        nume_persoana = "Subiect Anonim"
        if chat_id:
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("SELECT nume_persoana, tip_detectie FROM chaturi WHERE id = ?", (chat_id,))
                row = cursor.fetchone()
                if row:
                    nume_persoana = row[0]
                    tip_detectie = row[1] if row[1] else "mine"
                conn.close()
            except Exception as e:
                print(f"⚠️ Error reading chat settings for face: {e}")

        # Call visual context analysis using Groq Vision (combines safety & emotion classification)
        vision_context = None
        if image_base64:
            print("👁️ Running Groq Vision analysis...")
            vision_context = analyze_image_context(image_base64, tip_detectie=tip_detectie, nume_persoana=nume_persoana)
            
        # Overwrite/Supplement local prediction with Groq Vision emotions if successfully detected
        if vision_context and "emotions" in vision_context:
            print("🎨 Overriding Face-API.js emotions with Groq Vision precision...")
            emotions = vision_context.get("emotions", {})
            dominant_emotion = vision_context.get("dominant_emotion", "neutral")
            confidence = vision_context.get("confidence", 0.9)
            
            # Reconstruct processed face data for clinical indicator calculation
            face_processed_groq = {
                "status": "success",
                "confidence": confidence,
                "dominant_emotion": dominant_emotion,
                "emotions": emotions
            }
            
            # Calculate DSM-5 clinical indicators using the new, highly accurate Groq emotions
            from face import analyze_face_depression_indicators
            depression_indicators = analyze_face_depression_indicators(face_processed_groq)
            face_depression_score = depression_indicators.get("overall_face_depression_score", 0)
            
            # Map visual features notes
            facial_features["facial_expression"] = dominant_emotion
            facial_features["expression_confidence"] = confidence
            facial_features["detection_quality"] = "excellent" if confidence > 0.8 else "good"
            facial_features["notes"] = []
            
            # Append Groq Romanian description directly to notes
            if "description" in vision_context and vision_context["description"]:
                facial_features["notes"].append(vision_context["description"])
            
        # Incorporate visual context risk
        danger_detected = False
        if vision_context:
            if vision_context.get("gun_to_head_detected") or vision_context.get("rope_around_neck_detected") or vision_context.get("has_self_harm_intent") or vision_context.get("has_weapons"):
                danger_detected = True
                face_depression_score = 100
                depression_indicators["overall_face_depression_score"] = 100
                depression_indicators["sadness_indicator"] = 100
                depression_indicators["anxiety_indicator"] = 100
                depression_indicators["dissociation_indicator"] = 100
                
                # Build highly specific threat description based on what was found
                specific_threats = []
                if vision_context.get("gun_to_head_detected"):
                    specific_threats.append("armă îndreptată spre cap (gun to head)")
                if vision_context.get("rope_around_neck_detected"):
                    specific_threats.append("funie/ștreang în jurul gâtului (rope/noose around neck)")
                if vision_context.get("has_weapons") and not vision_context.get("gun_to_head_detected"):
                    specific_threats.append("prezența unei arme în imagine (weapon)")
                if vision_context.get("has_self_harm_intent") and not (vision_context.get("gun_to_head_detected") or vision_context.get("rope_around_neck_detected")):
                    specific_threats.append("intenție vizibilă de auto-vătămare (self-harm)")
                
                threat_desc = ", ".join(specific_threats) if specific_threats else "auto-vătămare sau arme în imagine"
                
                # Write direct, clear alert in notes
                if vision_context.get("emotional_context") == "blocked by safety filters" or "safety refusal" in vision_context.get("emotional_context", ""):
                    facial_features["notes"].append("🚨 AVERTISMENT CRITIC: Analiza a fost restricționată de filtrele de siguranță ale API-ului din cauza prezenței probabile de auto-vătămare sau arme!")
                else:
                    facial_features["notes"].append(f"🚨 AVERTISMENT CRITIC: S-a detectat vizual {threat_desc} în imagine!")
            else:
                multiplier = vision_context.get("context_risk_multiplier", 1.0)
                if multiplier > 1.0:
                    face_depression_score = int(face_depression_score * multiplier)
                    if vision_context.get("crying_or_tears_detected"):
                        depression_indicators["sadness_indicator"] = min(100, int(depression_indicators.get("sadness_indicator", 0) * 1.5))
                        facial_features["notes"].append("S-au detectat semne de plâns/lacrimi în analiza vizuală.")
                    if vision_context.get("visible_injuries"):
                        facial_features["notes"].append("S-au detectat indicii vizibile de răni/leziuni fizice.")
                    facial_features["notes"].append(f"Context emoțional vizual: {vision_context.get('emotional_context', 'distress')}")

        # If no imminent danger is detected visually, cap the face risk score at 79% (clinical limit for severe depression without active suicidal plan)
        if not danger_detected:
            face_depression_score = min(79, face_depression_score)
            depression_indicators["overall_face_depression_score"] = face_depression_score

        # Apply face score quarantine if last face score was high (>= 70%)
        if chat_id:
            last_face_score = get_last_face_score(chat_id)
            if last_face_score and last_face_score >= 70.0:
                face_depression_score = max(face_depression_score, last_face_score - 15.0)
                depression_indicators["overall_face_depression_score"] = face_depression_score
                print(f"⚠️ Face Quarantine: Prevent drop {last_face_score}% → {face_depression_score}%")

        # Check if any valid analysis occurred (either local Face-API succeeded or Groq Vision classified it)
        has_analysis = bool(face_detection) or (vision_context and "emotions" in vision_context)
        if not has_analysis and not danger_detected:
            return jsonify({
                "status": "error",
                "error": "Detectorul facial local nu a putut identifica nicio față, iar analiza vizuală nu a putut clasifica imaginea. Vă rugăm să folosiți o poză mai clară."
            }), 422

        # Map indicators keys for React component compatibility (DSM-5 Clinical Dimensions)
        depression_indicators_mapped = {
            "sadness": depression_indicators.get("sadness_indicator", 0),
            "indifference": depression_indicators.get("indifference_indicator", 0),
            "irritability": depression_indicators.get("irritability_indicator", 0),
            "anxiety": depression_indicators.get("anxiety_indicator", 0),
            "anhedonia": depression_indicators.get("anhedonia_indicator", 0),
            "overall_face_depression_score": face_depression_score
        }

        # Save face analysis to database
        if chat_id:
            try:
                conn = sqlite3.connect(DB_FILE, timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO face_analysis
                    (chat_id, image_url, depression_score, sadness, anxiety, irritability, anhedonia, dissociation, dominant_emotion, emotions, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    chat_id,
                    image_url,
                    face_depression_score,
                    depression_indicators.get("sadness_indicator", 0),
                    depression_indicators.get("anxiety_indicator", 0),
                    depression_indicators.get("irritability_indicator", 0),
                    depression_indicators.get("anhedonia_indicator", 0),
                    depression_indicators.get("indifference_indicator", 0), # store indifference in dissociation column
                    dominant_emotion,
                    json.dumps(emotions),
                    confidence
                ))
                
                conn.commit()
                conn.close()
                print("✅ Face analysis saved to database successfully (without mirroring to analize table)")
            except Exception as db_err:
                print(f"❌ Failed to save face analysis to DB: {db_err}")

        response = {
            "status": "success",
            "depression_indicators": depression_indicators_mapped,
            "overall_face_depression_score": face_depression_score,
            "facial_features": facial_features,
        }
        
        # If chat_id provided, combine with text/voice analysis
        if chat_id:
            print("📊 Combining with historical analysis...")
            last_score, _ = get_last_score(chat_id)
            text_score = last_score if last_score else 0
            voice_score = 0
            multimodal = combine_voice_and_face_scores(voice_score, face_depression_score, text_score)
            response["combined_multimodal"] = multimodal
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"❌ Face analysis error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


# ─── MULTIMODAL ANALYSIS ENDPOINT ────────────────────────────────────────────

@app.route("/analyze-multimodal", methods=["POST"])
def analyze_multimodal():
    """
    Combined analysis of voice, face, and text
    
    Request body:
    {
        "chat_id": "required",
        "audio": "optional_base64_audio",
        "face_detection": "optional_face_api_data",
        "text": "optional_manual_text"
    }
    
    Returns:
    {
        "status": "success",
        "voice_analysis": { voice scores },
        "face_analysis": { face scores },
        "text_analysis": { text scores },
        "combined_score": 0-100 (weighted average),
        "confidence": 0-100,
        "recommendations": { advice based on combined analysis }
    }
    """
    
    if not (VOICE_ENABLED or FACE_ENABLED):
        return jsonify({"error": "Voice/Face modules not enabled"}), 500
    
    try:
        data = request.json
        chat_id = data.get("chat_id")
        audio_base64 = data.get("audio")
        face_detection = data.get("face_detection")
        manual_text = data.get("text", "").strip()
        
        if not chat_id:
            return jsonify({"error": "chat_id is required"}), 400
        
        results = {
            "chat_id": chat_id,
            "voice_analysis": None,
            "face_analysis": None,
            "text_analysis": None,
            "combined_score": 0,
            "confidence": 0,
        }
        
        voice_score = 0
        face_score = 0
        text_score = 0
        
        # Process voice if provided
        if audio_base64 and VOICE_ENABLED:
            print("🎤 Analyzing voice...")
            audio_binary = base64.b64decode(audio_base64)
            voice_result = process_voice_input(audio_binary)
            if voice_result.get("status") == "success":
                voice_score = voice_result.get("analysis", {}).get("overall_voice_indicator", 0)
                results["voice_analysis"] = voice_result
        
        # Process face if provided
        if face_detection and FACE_ENABLED:
            print("😊 Analyzing face...")
            face_result = process_face_input(face_detection)
            if face_result.get("status") == "success":
                face_score = face_result.get("depression_indicators", {}).get("overall_face_depression_score", 0)
                results["face_analysis"] = face_result
        
        # Process text (from audio transcript or manual input)
        text_to_analyze = manual_text
        if not text_to_analyze and audio_base64:
            # Try to get transcript from voice result
            text_to_analyze = results.get("voice_analysis", {}).get("transcript", "")
        
        if text_to_analyze:
            print("📝 Analyzing text...")
            istoric_context = get_full_chat_history_for_diagnostic(chat_id)
            last_score, _ = get_last_score(chat_id)
            linguistic_markers = analyze_linguistic_markers(text_to_analyze)
            sarcasm_score = detect_sarcasm_and_context(text_to_analyze, last_score)
            
            nume_persoana, tip_detectie = get_chat_details(chat_id)
            ai_data = call_llm_api(text_to_analyze, istoric_context, last_score, None, linguistic_markers, sarcasm_score, tip_detectie, nume_persoana)
            text_analysis = calculeaza_scor(ai_data, chat_id, text_to_analyze) if ai_data else None
            
            if text_analysis:
                text_score = text_analysis.get("score", 0)
                results["text_analysis"] = text_analysis
        
        # Combine all modalities
        if audio_base64 and face_detection and manual_text:
            # All three available
            combined_score = int(text_score * 0.50 + voice_score * 0.25 + face_score * 0.25)
            # Agreement score
            max_diff = max(abs(text_score - voice_score), abs(text_score - face_score), abs(voice_score - face_score))
            confidence = max(0, 100 - max_diff)
        elif text_to_analyze:
            # Text + one other
            combined_score = int(text_score * 0.50 + (voice_score + face_score) * 0.25)
            confidence = 75
        elif voice_score and face_score:
            # Voice + face only
            combined_score = int((voice_score + face_score) / 2)
            confidence = 60
        else:
            combined_score = voice_score or face_score or text_score
            confidence = 50
        
        results["combined_score"] = combined_score
        results["confidence"] = confidence
        
        return jsonify({
            "status": "success",
            **results
        }), 200
        
    except Exception as e:
        print(f"❌ Multimodal analysis error: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)