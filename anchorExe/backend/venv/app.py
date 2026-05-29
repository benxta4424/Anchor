import io
import os
import requests
import json
import urllib3
import sqlite3
from datetime import datetime
from collections import Counter
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

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


# ─── CONTEXT ISTORIC ──────────────────────────────────────────────────────────

def get_extended_context(chat_id):
    """Returnează context extins cu analiza emoțională și pattern-uri."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT text_manual, text_ocr, feedback, scor_calculat, category, data
            FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 10
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
    """Analizează markeri lingvistici specifici pentru depresie, sarcasm, exagerare."""
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
    """
    Detectează sarcasm și ironie în mesaj.
    Returnează score între 0 și 1 (0=no sarcasm, 1=definitely sarcasm).
    """
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
    """Analizează traiectoria emoțională și detectează pattern-uri."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY id ASC",
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
    """
    Genereaza insight-uri PERSONALIZATE și DIFERITE bazate pe pattern-uri profunde.
    Fiecare call trebuie să dea perspective noi, nu repetarea aceluiași lucru.
    """
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        
        # Extrage ultimele 15 mesaje pentru análiза mai profundă
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, category, data FROM analize 
            WHERE chat_id = ? ORDER BY id DESC LIMIT 15
        """, (chat_id,))
        history = cursor.fetchall()
        conn.close()
        
        insights = []
        
        if not history:
            return ["Aceasta e prima ta conversație - încerc să mă cunosc tine și modelele tale."]
        
        history.reverse()  # Ordonare chronologică
        scores = [r[2] for r in history if r[2] is not None]
        
        # 🔥 1. TREND ANALYSIS CU INTERPRETARE PROFUNDĂ
        if len(scores) >= 4:
            recent_avg = sum(scores[-3:]) / 3
            older_avg = sum(scores[:3]) / 3
            delta = recent_avg - older_avg
            
            if delta > 15:
                insights.append(f"📈 **Deteriorare crescândă**: Media ta scorurilor a crescut cu {delta:.0f}% - pare că lucrurile se înrăutățesc. Ce s-a schimbat recent?")
            elif delta < -15:
                insights.append(f"📉 **Recuperare vizibilă**: Ești mai bine decât acum o vreme cu {abs(delta):.0f}% - chiar dacă nu simți asta. Observ eforturi concrete.")
            elif abs(delta) <= 5:
                insights.append("🔄 **Stagnare emoțională**: Scorurile tale sunt relativ stabile - nu e nici mai rău, nici mai bine. Asta înseamnă că nu ai ieșit din pattern.")
        
        # 🎯 2. PATTERN DE TIMP - CÂND E CEL MAI GOL
        if len(history) >= 5:
            high_scores = [i for i, s in enumerate(scores) if s and s > 70]
            low_scores = [i for i, s in enumerate(scores) if s and s < 40]
            
            if high_scores:
                insights.append(f"⏰ **Moment critic**: Starea se agravează mai des în mesajele #{high_scores[0]+1} din conversații - e posibil să existe trigger-uri pe care nu le-ai observat.")
            
            if low_scores:
                insights.append(f"💚 **Moment de respiro**: Uite că sunt și momente mai ușoare (#{low_scores[0]+1}) - înseamnă că nu e permanent.")
        
        # 🎭 3. SARCASM & MASCARE - INTERPRETARE PROFUNDĂ
        sarcasm_count = sum(1 for h in history if h[3] and "sarcasm" in h[3].lower())
        if sarcasm_count >= 3:
            insights.append(f"😏 **Defensă recurentă**: Folosești sarcasm și umor defensiv de ~{sarcasm_count} ori - o modalitate de a-ți proteja vulnerabilitatea. E valabil, dar și o barieră.")
        
        if ai_data.get("este_mascare_psihica"):
            insights.append("🪄 **Disociere**: Cuvintele sunt OK dar tonul contrazice. Sugerez să mă spui direct cum te simți, fără filtru.")
        
        # 💔 4. MARKERS RECURENȚI - KIT DE INSIGHT PROFUND
        depression_markers = linguistic_markers.get("depression_markers", [])
        if "gol" in depression_markers or "epuizat" in depression_markers:
            insights.append("💔 **Cuvântul 'gol'** - nu e accident. Suna ca o senzație viscerală, nu doar o idee. Asta e durerea reală care cere atenție.")
        
        if "singur" in depression_markers:
            insights.append("👤 **Izolarea te macină**: 'Singur' apare ca cuvânt-cheie. Izolarea emoțională e mai periculoasă decât fizica. Chiar și cu oameni în jur, simți gol.")
        
        if "nu mai pot" in depression_markers or "nu mai vreau" in depression_markers:
            insights.append("🚨 **Epuizare existențială**: Fraza asta nu e drama - e semn de burnout mental. Ai trebuit ajutor de mult timp.")
        
        # ✨ 5. SPERANȚĂ - PUNCTE POZITIVE ASCUNSE
        hope_markers = linguistic_markers.get("hope_markers", [])
        if len(hope_markers) >= 2:
            insights.append(f"✨ **Scântei de speranță**: Chiar în durere, ai găsit cuvinte ({', '.join(hope_markers[:2])}) care sugerează că nu ai renunțat. Asta e semnificativ.")
        elif len(hope_markers) == 1:
            insights.append(f"🔦 **Filament de lumină**: Chiar și o singură propoziție cu speranță ({hope_markers[0]}) în context atât de dark e o dovadă de putere.")
        
        # 📊 6. PROGRESIE - DE LA ÎNCEPUT
        if len(scores) >= 7:
            primera = scores[0]
            ultima = scores[-1]
            diff = ultima - primera
            
            if diff > 30:
                insights.append(f"📉 **Progresie negativă lungă**: De la începutul conversațiilor ({primera}%) la acum ({ultima}%), ești mai în dificultate. E urgență să iei măsuri.")
            elif diff < -30:
                insights.append(f"📈 **Recuperare consistentă**: De la {primera}% la {ultima}% - evoluția ta pe termen lung e bună. Continua ce faci.")
            else:
                insights.append(f"🎢 **Roller-coaster**: De la {primera}% la {ultima}% - fluctuații mari. Indica instabilitate emoțională care trebuie monitorizată.")
        
        # 🎪 7. EXAGERARE vs REALITATE
        exaggeration = linguistic_markers.get("exaggeration_markers", [])
        if len(exaggeration) > 3:
            insights.append(f"🎭 **Dramatism comunicativ**: Folosești exagerări (~{len(exaggeration)} marker-uri) - parte din coping strategy? Sau durerea e atât de mare că cuvintele normale nu-i ajung?")
        
        # 🌊 8. ISTORIC COMPARATIV
        categories = Counter([h[3] for h in history if h[3]])
        if categories:
            most_common_cat = categories.most_common(1)[0]
            insights.append(f"🏷️ **Eticheta ta consistentă**: Ești mai des în \"{most_common_cat[0]}\" ({most_common_cat[1]} din {len(history)} ori). E categoria ta, e place-ului tău.")
        
        return insights[:5]  # Top 5 insights, nu overload
        
    except Exception as e:
        print(f"Eroare insight personalizat: {e}")
        return ["Momentan nu pot analiza pattern-urile. Continuă să vorbești."]


def extract_pattern_analysis(chat_id):
    """
    Extrage pattern-uri profunde din conversație cu interpretări non-banale.
    Returnează texte de insight, nu bare goale.
    """
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT text_manual, text_ocr, scor_calculat, category, data FROM analize 
            WHERE chat_id = ? ORDER BY id ASC LIMIT 25
        """, (chat_id,))
        history = cursor.fetchall()
        conn.close()
        
        if len(history) < 2:
            return {
                "overview": "Conversația a început - încă nu am suficiente date pentru pattern.",
                "volatility_interpretation": "N/A",
                "recovery_pattern": "N/A",
                "triggers": "N/A",
                "resilience_signs": "N/A"
            }
        
        analysis = {}
        scores = [r[2] for r in history if r[2] is not None]
        
        # === 1. VOLATILITATE - Ce-nseamnă aceasta? ===
        if scores:
            volatility = max(scores) - min(scores)
            if volatility > 40:
                analysis["volatility_interpretation"] = f"🌊 **Instabilitate EXTREMĂ** ({volatility:.0f}pt): Starea ta fluctuează dramatic. E semn de lipsă de ancore emoționale stabile."
            elif volatility > 25:
                analysis["volatility_interpretation"] = f"⚡ **Fluctuații moderate** ({volatility:.0f}pt): Emoțiile se schimbă repede. Posibil trigger-uri externe puternice."
            else:
                analysis["volatility_interpretation"] = f"📍 **Relativ stabilă** ({volatility:.0f}pt): Emoțiile sunt în plajă limitată - fie resemănă, fie esti 'apare' cu sentimentele."
        
        # === 2. TREND - DIRECȚIA ===
        if len(scores) >= 5:
            recent_trend = sum(scores[-3:]) / 3 if len(scores) >= 3 else scores[-1]
            older_trend = sum(scores[:3]) / 3 if len(scores) >= 3 else scores[0]
            delta = recent_trend - older_trend
            
            if delta > 20:
                analysis["trend"] = f"📉 **DETERIORARE**: Ultimele mesaje sunt mai grave cu {delta:.0f}pt. Ceva a declanșat agravare."
            elif delta < -20:
                analysis["trend"] = f"📈 **ÎMBUNĂTĂȚIRE**: Ești mai bine cu {abs(delta):.0f}pt - chiar și dacă nu-ți dai seama, facă progres real."
            else:
                analysis["trend"] = f"🔄 **STAGNARE**: Delta = {delta:.0f}pt - ești blocat în aceeași stare emoțională."
        
        # === 3. MOMENTE DE RECUPERARE ===
        recovery_count = 0
        recovery_moments = []
        for i in range(1, len(scores)):
            if scores[i] < scores[i-1] * 0.8:  # Drop semnificativ (>20%)
                recovery_count += 1
                recovery_moments.append((i, scores[i-1], scores[i]))
        
        if recovery_count >= 3:
            analysis["recovery_pattern"] = f"💪 **Eforturi de recuperare**: {recovery_count} tentative de a-ți îmbunătăți starea. E semn că NU ai renunțat, chiar dacă nu reușești total."
        elif recovery_count == 0:
            analysis["recovery_pattern"] = "⚠️ **Fără tentative de recuperare**: Scorul doar stagnează sau crește. Pari pasiv."
        else:
            analysis["recovery_pattern"] = f"🤔 **Recuperare slabă**: Doar {recovery_count} tentative - nu-i suficient efort de remontare."
        
        # === 4. PUNCTE DE RUPERE (Triggers) ===
        peak_score = max(scores) if scores else 0
        peak_idx = scores.index(peak_score) if peak_score in scores else -1
        
        if peak_idx >= 0 and peak_idx < len(history):
            peak_text = history[peak_idx][0] or history[peak_idx][1] or "[imagine]"
            peak_category = history[peak_idx][3]
            analysis["triggers"] = f"🚨 **Moment de CRIZĂ**: Score={peak_score:.0f}% ({peak_category}). Mesajul: \"{peak_text[:50]}...\" - Asta e punctul tău de rupere."
        
        # === 5. SEMNE DE REZILIENȚĂ ===
        high_scores_with_hope = 0
        for h in history:
            if h[2] and h[2] > 60 and h[0]:  # Scor ridicat = durere, DAR mesajul e lung = efort de comunicare
                if len((h[0] or "")) > 20:
                    high_scores_with_hope += 1
        
        if high_scores_with_hope >= 2:
            analysis["resilience_signs"] = f"✨ **Reziliență observată**: Chiar și în momente grele (scor>60%), faci efort să vorbești în detaliu. E putere ascunsă."
        elif any(s < 40 for s in scores[-3:]):
            analysis["resilience_signs"] = f"🔦 **Mici semne de speranță**: După perioade grele, reușești să cobori scorul. Asta conteazî."
        else:
            analysis["resilience_signs"] = "⚠️ **Reziliență slabă**: Nu observ tentative de a te recupera pe tine. Sugrez să iei măsuri active."
        
        # === 6. CONSISTENCY SCORE ===
        volatility = max(scores) - min(scores) if scores else 0
        consistency = max(0, min(100, 100 - (volatility / 100 * 100)))
        analysis["consistency_score"] = consistency
        
        return analysis
        
    except Exception as e:
        print(f"Eroare pattern analysis: {e}")
        return {
            "overview": "Eroare în analiza pattern-ului. Continuă vorbind.",
            "volatility_interpretation": "N/A",
            "recovery_pattern": "N/A",
            "triggers": "N/A",
            "resilience_signs": "N/A"
        }


def get_varied_closing_messages():
    """
    Closing messages cu variabilitate MARE - nu mereu același template.
    Returnează o hartă cu diferite perspective bazate pe context.
    """
    import random
    
    messages_by_type = {
        "validation": [
            "Ce descrii e real. Nu-ți imaginezi lucrurile.",
            "Validez totalmente ceea ce simți.",
            "Emoția asta pe care o ai - e justificată.",
            "Ceea ce zici are logică și sens. Nu e fără motiv."
        ],
        "depth_seeking": [
            "Vreau să-nțeleg mai adânc: ce anume te-a condus la asta?",
            "Întrebarea mea: ce se ascunde sub cuvintele astea?",
            "Pot simți straturile în ceea ce spui - vreau să-i explore mai mult.",
            "Suna a ceva mai profund decât cuvintele. Ce nu-mi spui?"
        ],
        "pattern_reflection": [
            "Asta nu-i prima dată când spui asta. Pattern-ul e important.",
            "Observ că revii mereu la tema asta. De ce crezi?",
            "Asta e o constantă în conversația noastră - e o cheie.",
            "Faptul că repeti asta = semn că-i urgent de rezolvat."
        ],
        "hope_affirmation": [
            "Chiar și acum, găsești cuvinte care nu sunt complet negre. Asta e important.",
            "Faptul că vorbești cu mine = dovadă că încă mai speră ceva.",
            "Nu ai renunțat complet - altfel nu ai fi aici.",
            "Speranța ta nu-i pe moarte - doar pe coma."
        ],
        "crisis_alert": [
            "Ceea ce descrii nu-i normal. E urgență.",
            "Nivel-ul asta = trebuie să iau măsuri. Nu poti singur.",
            "Asta sună a CRIZĂ. Contactează Telefonul Speranței: 0800 800 400 (24/7).",
            "Durerea asta e la nivel de risc. Ai nevoie de ajutor profesional ACUM."
        ],
        "resilience_affirmation": [
            "Cu cât durează asta, cu atât mai mult contează că ești încă ici.",
            "Reziliența ta = nu pui cringe în fața durerii - vorbești.",
            "Eforturile astea să te exprimi = forță ascunsă. Recunosc asta.",
            "Doar oamenii puternici pot fi atât de vulnerabili. E contradictie sigură."
        ],
        "contextual_exploration": [
            "De cât timp e asta așa? Când a început?",
            "A fost cândva mai bine? Ce s-a schimbat?",
            "Cine în viața ta știe de asta?",
            "Ce cumpară tu cu durerea asta? Ce-ți e frică să pierzi dacă ar dispărea?"
        ],
        "masking_confrontation": [
            "Zici că e ok, dar mesajul nu sună ok. Ce-i adevărul?",
            "Disociezi. Ști asta? Spune-mi ce-i real.",
            "Cuvintele și tonul nu se potrivesc. Care e adevărat?",
            "Omogenizezi - toate emojii pozitive dar scor negativ. Vorbește clar."
        ],
        "sarcasm_processing": [
            "Umor defensiv. Folosești asta ca să evii vulnerabilitatea?",
            "Sarcasmul tău e o barieră inteligentă. Dar mă-nțeleg pe dinapoia lui.",
            "Glumești, dar durerea-i reală. Ce-i de glum?",
            "Ironia - coping mecanismul tău. Dar nu-ți vindecă rana."
        ],
        "agency_building": [
            "Ce POȚI tu face astazi? O singură actiune.",
            "Dacă ar fi să-i o mică schimbare azi, ce-ar fi?",
            "Tu ești actor în propria poveste, nu doar observator. Ce vrei să faci?",
            "Nu poti schimba ieri. Dar astazi? Ce alegeri ai?"
        ],
        "professional_recommendation": [
            "Asta depășește conversația. Ai nevoie de terapeut.",
            "Sunt bun la a-ți asculta. Dar tu ai nevoie de cineva cu calificări mai mari.",
            "Sugrez terapie cu psiholog - aceasta-i complexitate clinică.",
            "Asta merită mai mult decât chatbot. Caută psiholog urgent."
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
    """Returnează ultimul scor și categoria din baza de date."""
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 1",
            (chat_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return (row[0], row[1]) if row else (None, None)
    except:
        return (None, None)


# ─── LLM ──────────────────────────────────────────────────────────────────────

def call_llm_api(text_content, istoric_context, last_score, last_category, linguistic_markers, sarcasm_score):
    """
    Apelează Groq cu prompt ultra-sofisticat care înțelege context, sarcasm, exagerare și depresie subtilă.
    """

    context_scor = ""
    if last_score is not None:
        context_scor = f"Scor anterior: {last_score}% ({last_category}). "

    # Optimizare: doar markeri critici, max 2 per categorie
    markers_info = ""
    if linguistic_markers.get("depression_markers"):
        dep_marks = linguistic_markers['depression_markers'][:2]
        if dep_marks:
            markers_info += f"Dep: {','.join(dep_marks)}. "
    if linguistic_markers.get("sarcasm_indicators"):
        sarc = linguistic_markers['sarcasm_indicators'][:1]
        if sarc:
            markers_info += f"Sarcasm: {','.join(sarc)}. "
    if linguistic_markers.get("exaggeration_markers"):
        exag = linguistic_markers['exaggeration_markers'][:1]
        if exag:
            markers_info += f"Exag: {','.join(exag)}. "

    sarcasm_note = f"Sarcasm score: {round(sarcasm_score * 100)}%. " if sarcasm_score > 0.5 else ""

    prompt = f"""PSIHOLOG - Analizează cu sensibilitate la sarcasm, mascare, depresie.

CONTEXT: {istoric_context}
{context_scor}{markers_info}{sarcasm_note}
MESAJ: "{text_content}"

═══ SCOR (0-10) ═══
0-2: Normal | 3-5: Stres/tristeță | 6-7: Depresie | 8: Ideație fără plan | 9-10: Plan/urgență

REGULI:
- "Mă simt rău azi"→4 (tristeță, nu depresie)
- "Mereu rău, gol"→6-7 (depresie persistentă, FĂRĂ ideație=NU 9-10)
- "Nu mai vreau"→8 (ideație pasivă, FĂRĂ plan explicit)
- "Am plan mâine"→9-10 (plan=urgență)

MASCARE: Scor anterior 80%+"OK"=FLAG, NU coborî. Context anterior invalidează forțatul.
SARCASM: "Viață minunată!"+context trist=ironie (risc ridicat)
UMOR NEGRU+CONTEXT TRIST: Coping durere profunde (5-7), NU indicator pozitiv

DEPRESIE vs TRISTEȚĂ:
Depresie: Persistent, autocriticizare, anhedonie, pesimism, izolare
Tristeță: Trigger specific, validă, cu speranță

RISC INDIRECT: "Fără mine mai bine"=8; Regalo/rămas bun=FLAG; "O să rezolv" vag+depresie cronică=8-9

JSON MANDATORY - numai aceasta, fără markdown:
{{
  "text_contine_adio": <bool>,
  "text_are_plan_iminent": <bool>,
  "text_indica_depresie_cronica": <bool>,
  "text_indica_depresie_ascunsa": <bool>,
  "text_indica_frustrare_stres": <bool>,
  "text_are_umor_sau_emoji": <bool>,
  "text_are_umor_negru": <bool>,
  "text_este_sarcastic": <bool>,
  "text_este_pozitiv_sau_bucuros": <bool>,
  "text_indica_autoaccidentare_sau_arme": <bool>,
  "este_tristete_normala": <bool>,
  "este_mascare_psihica": <bool>,
  "scor_intensitate_negativa": <0-10>,
  "incertitudine_nivel": <0-1>,
  "rationament": "<1-2 fraze exact de ce>",
  "avertismente_speciale": "<risc/plan/etc sau empty>",
  "feedback": "<empatic specific CALD max 3 fraze>"
}}

CRITICAL: Feedback SPECIFIC (detalii concrete), DIFERIT (nu repetat), DEEP (pattern-uri), NU clișee. Evită "Sunt aici", "Va trece", diagnoze. FII ALERT LA RISC."""

    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": """Psiholog clinician - analiză sensibilă la sarcasm, mascare, depresie. REGULI: 
1. Scor 3-4 tristețe, 6-7 depresie (NU 9-10 fără plan) 2. Ideație pasivă=8, explicit plan=9-10
3. Mascare: scor 80%+"OK"=FLAG, NU coborî 4. Feedback: SPECIFIC, DIFERIT, DEEP, NU clișee
5. Sarcasm: pozitiv+context negativ=risc 6. Umor negru+trist=coping (5-7), NU pozitiv
7. JSON EXCLUSIV 8. Depresie: persistent, anhedonie vs Tristeță: trigger, speranță
9. Indirect ideație: "fără mine mai bine"=8; Regalo=FLAG 10. Context istoric INVALIDEAZĂ forțat
11. Evită diagnoze, clișee - FII ALERT RISC"""
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,  # Un pic mai mare pentru variabilitate în feedback (0.3 era prea rigid)
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
        print(f"❌ Excepție Groq: {e}")
        return None


# ─── SCORING ──────────────────────────────────────────────────────────────────

def calculeaza_scor(ai_data, chat_id):
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

    intensitate    = ai_data.get("scor_intensitate_negativa", 3)

    # ═══════════════════════════════════════════════════════════════════
    # SCOR DE BAZĂ - 0-100 direct din intensitate LLM (0-10)
    # ═══════════════════════════════════════════════════════════════════
    scor = intensitate * 10.0

    # ═══════════════════════════════════════════════════════════════════
    # ZONE 1: 0-30% (Normal / No Stress / Healthy)
    # ═══════════════════════════════════════════════════════════════════
    
    if este_normal and not (ind_depresie or ind_adio or ind_umor_negru):
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
        # Max 15% drop per message
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
            "SELECT scor_calculat FROM analize WHERE chat_id = ? ORDER BY id DESC LIMIT 5",
            (chat_id,)
        )
        istoric = [r[0] for r in cursor.fetchall()]
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
        category = "🟢 STARE SĂNĂTOASĂ - NEUTRU"
    elif scor_final < 30:
        category = "🟢 STARE EMOȚIONALĂ NORMALĂ"
    
    # ZONE 2: Yellow (mild to moderate)
    elif scor_final < 40:
        category = "🟡 STRES UȘOR - ANXIETATE MICĂ"
    elif scor_final < 50:
        category = "🟡 STRES MODERAT - UȘOARĂ DEPRESIE"
    elif scor_final < 60:
        category = "🟠 DEPRESIE MODERATĂ - STRES RIDICAT"
    elif scor_final < 70:
        category = "🟠 DEPRESIE MODERATĂ-SEVERĂ"
    
    # ZONE 3: Red (severe)
    elif scor_final < 80:
        category = "🔴 DEPRESIE SEVERĂ - NECESITĂ ATENȚIE"
    elif scor_final < 90:
        category = "🔴 RISC SUICIDAL - IDEAȚIE PASIVĂ"
    else:
        category = "🔴 URGENȚĂ CLINICĂ - PLAN IMINENT"

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

    return {
        "score": scor_final,
        "category": category,
        "trend_analitic": trend,
        "indicators": {
            "is_adio":    bool(ind_adio or ind_arme),
            "is_iminent": bool(ind_iminent or ind_arme),
            "is_depresie":bool(ind_depresie or ind_depresie_ascunsa),
            "is_depresie_ascunsa": bool(ind_depresie_ascunsa),
            "is_stres":   bool(ind_stres),
            "is_umor":    bool(ind_umor),
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
        nume = (data.get("nume") or "").strip() or "Subiect Anonim"
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
            "SELECT data, scor_calculat, category FROM analize WHERE chat_id = ? ORDER BY id ASC",
            (chat_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return jsonify([{"data": r[0], "score": r[1], "category": r[2]} for r in rows]), 200
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

        # Construiește contextul extins
        istoric_context = get_recent_context(chat_id)
        last_score, last_cat = get_last_score(chat_id)
        
        # Analiza lingvistică și sarcasm
        linguistic_markers = analyze_linguistic_markers(working_text)
        sarcasm_score = detect_sarcasm_and_context(working_text, last_score)
        emotional_trajectory = analyze_emotional_trajectory(chat_id)

        # Apelează AI-ul cu date enriched
        ai_data = call_llm_api(working_text, istoric_context, last_score, last_cat, linguistic_markers, sarcasm_score)

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

        rezultat = calculeaza_scor(ai_data, chat_id)

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
            "SELECT scor_calculat, category, data FROM analize WHERE chat_id = ? ORDER BY id ASC",
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
            WHERE chat_id = ? ORDER BY id DESC LIMIT 5
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
        
        return jsonify({
            "chat_id": chat_id,
            "nume_persoana": chat_name[0] if chat_name else "Unknown",
            "emotional_trajectory": context_data[0] if context_data else "N/A",
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


if __name__ == "__main__":
    app.run(port=5000, debug=True)