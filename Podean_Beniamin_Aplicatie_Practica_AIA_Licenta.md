# Ghid de Instalare, Compilare şi Lansare: Sistemul Multimodal Anchor
**Student:** Podean Beniamin  
**Specializarea:** Automatică şi Informatică Aplicată (AIA) / Ingineria Sistemelor (IS)  
**Instituţie:** Universitatea Politehnica Timişoara (UPT)  

---

## 1. Adresa Repository-ului Git
Codul sursă al proiectului este găzduit şi versionat la adresa:
👉 **[https://gitlab.upt.ro/beniamin.podean/Anchor](https://gitlab.upt.ro/beniamin.podean/Anchor)**

*(Notă: Repository-ul conţine istoricul complet al dezvoltării, structurat fără fişiere binare compilate sau directoare grele precum `node_modules` şi `__pycache__`, acestea fiind excluse prin reguli `.gitignore` standard).*

---

## 2. Descrierea Livrabilelor Proiectului
Structura proiectului este împărţită clar între frontend (React) şi backend (Flask), ambele localizate în directorul `/anchorExe`:

*   **Frontend (React 19 / Vite):** Directorul principal `/anchorExe`
    *   `/src`: Conţine componentele vizuale ale aplicaţiei (panoul de control - dashboard, chaturile active, graficele interactive bazate pe Chart.js, componenta de achiziţie audio `EnhancedVoiceComponent.jsx` şi cea video `EnhancedFaceComponent.jsx`).
    *   `/public`: Resursele statice accesibile direct în browser, inclusiv folderul `/models` unde sunt stocate fişierele binare ale reţelelor neurale locale Face-API.js (`TinyFaceDetector` şi `FaceExpressionNet`).
    *   `package.json`: Specificaţia dependenţelor npm şi a scripturilor de compilare/rulare.
    *   `vite.config.js`: Configuraţia mediului de dezvoltare rapid Vite.
*   **Backend (Flask / Python 3):** Directorul `/anchorExe/backend/venv`
    *   `app.py`: Reprezintă nucleul aplicaţiei backend (API Gateway). Orchestrează cererile HTTP POST şi GET de la client, efectuează apelurile API externe către Groq LPU, şi coordonează procesarea de date locale.
    *   `face.py`: Modulul care preia ponderile biometrice faciale calculate de frontend şi le mapează pe dimensiunile de analiză emoţională DSM-5.
    *   `voice.py`: Modulul care procesează semnalele audio, rulând algoritmi DSP offline (folosind NumPy şi Librosa) pentru extragerea volumului (RMS), tempoului (BPM), pitch-ului şi clarităţii vocii.
    *   `mindscan_history.db`: Baza de date relaţională locală SQLite, conţinând schemele pentru cele 6 tabele (`chaturi`, `analize`, `voice_analysis`, `face_analysis`, `multimodal_analysis`, `conversation_context`).
    *   `.env`: Fişierul de configurare a cheilor secrete şi calea utilitarelor locale (ex: Tesseract OCR).

---

## 3. Cerinţe de Sistem (Prerequisites)
Înainte de instalare, asiguraţi-vă că aveţi instalate următoarele utilitare pe maşina gazdă:
1.  **Node.js** (versiunea 18.0 sau mai nouă)
2.  **Python** (versiunea 3.10 sau mai nouă)
3.  **Tesseract OCR** (utilitarul de recunoaştere optică a textului din imagini). Pe Windows, descărcaţi instalatorul şi reţineţi calea executabilului (implicit: `C:\Program Files\Tesseract-OCR\tesseract.exe`).

---

## 4. Paşii de Instalare şi Configurare

### Pasul A: Configurare Backend (Python / Flask)
1.  Deschideţi o consolă (PowerShell sau Terminal) şi navigaţi în folderul backend:
    ```bash
    cd c:\Users\Podean Beniamin\Desktop\licenta\Anchor\anchorExe\backend\venv
    ```
2.  Creaţi un mediu virtual de Python (venv):
    ```bash
    python -m venv venv
    ```
3.  Activaţi mediul virtual:
    *   **Pe Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **Pe Linux / macOS:**
        ```bash
        source venv/bin/activate
        ```
4.  Instalaţi toate bibliotecile necesare:
    ```bash
    pip install flask flask-cors groq numpy scipy librosa pytesseract pillow python-dotenv standard-aifc standard-chunk standard-sunau audioop-lts
    ```
5.  Creaţi sau editaţi fişierul `.env` din folderul backend (`/anchorExe/backend/venv/.env`) şi introduceţi configuraţiile:
    ```env
    GROQ_API_KEY=cheia_ta_secreta_groq_api
    TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
    PORT=5000
    ```

### Pasul B: Configurare Frontend (React / Vite)
1.  Deschideţi o altă consolă şi navigaţi la rădăcina proiectului frontend:
    ```bash
    cd c:\Users\Podean Beniamin\Desktop\licenta\Anchor\anchorExe
    ```
2.  Instalaţi modulele de nod (dependenţele React):
    ```bash
    npm install
    ```

---

## 5. Paşii de Compilare şi Lansare a Aplicaţiei

Aplicaţia poate fi lansată atât în regim de dezvoltare (Live Server), cât şi compilată complet pentru producţie.

### Lansare în Regim de Dezvoltare (Development)

1.  **Pornire Backend (Flask):**
    În consola de backend (cu mediul virtual `venv` activat), lansaţi scriptul principal:
    ```bash
    python app.py
    ```
    *Serverul va porni pe `http://localhost:5000`.*

2.  **Pornire Frontend (Vite):**
    În consola de frontend, rulaţi serverul de dezvoltare:
    ```bash
    npm run dev
    ```
    *Aplicaţia va porni instantaneu pe portul implicit `http://localhost:5173`.*

---

### Compilare pentru Producţie (Production Build)

Dacă doriţi compilarea şi optimizarea codului frontend într-un pachet static de producţie (HTML/JS/CSS optimizat):

1.  În consola de frontend (`/anchorExe`), rulaţi scriptul de compilare:
    ```bash
    npm run build
    ```
    *Acest pas va genera folderul `/anchorExe/dist` care conţine toate fişierele statice, comprimate şi pregătite pentru a fi servite pe orice server web de producţie (Nginx, Apache).*

2.  Pentru a previzualiza local pachetul compilat de producţie, rulaţi:
    ```bash
    npm run preview
    ```
    *Browserul se va deschide pe portul indicat de Vite (de regulă `http://localhost:4173`), servind fişierele compilate din `/dist`.*
