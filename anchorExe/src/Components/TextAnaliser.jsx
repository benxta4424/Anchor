// deci ca sa imi fie mai usor, o sa incerc sa fac un script de pyuthon care face text recognition din poza si mi l trimite ca si text aici ca sa nu incarc AI ul prea mukt
// deci eu o sa primesc SS cu textul unui prieten si scriptul o sa scoata textul din poza ca sa nu trebuiasca sa o faca AI ul
// dupa ce scoate scriptul, o sa trimit in backend API ul AI ului mesajul in sine si o sa l pun sa detecteze asa, pare mnai usor sincer
import { useState } from "react";


export default function TextAnaliser() {
    const [rawText, setRawText] = useState("");
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
        }
    };

    const handleRemoveImage = () => {
        setFile(null);
        setPreview(null);
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!rawText.trim() && !file) {
                return alert("Scrie un mesaj sau încarcă o imagine!");
            }

            setLoading(true);
        const formData = new FormData();
        
       
        if (rawText.trim()) {
            formData.append("rawText", rawText.trim());
        }
        
        if (file) {
            formData.append("image", file);
        }

        try {
            const response = await fetch("http://localhost:5000/analyze-text", {
                method: "POST",
                body: formData,
            });
            const data = await response.json();
            setResult(data);
            
          
            setRawText("");
            setFile(null);
            setPreview(null);
        } catch (error) {
            console.error("Eroare:", error);
            alert("Nu s-a putut conecta la serverul Flask (port 5000).");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="analiserWrapper">
            <header className="analiserHeader">
                <h1>Mind<span>Scan</span> Chat</h1>
                <p>Scrie un mesaj sau încarcă un screenshot pentru analiză instantanee.</p>
            </header>

            <div className="analiserGrid">
                
                <div className="chatInterfaceCard">
                    <div className="chatPreviewArea">
                        {preview ? (
                            <div className="imagePreviewContainer">
                                <img src={preview} alt="Preview" className="chatImgPreview" />
                                <button className="removeImgBtn" onClick={handleRemoveImage}>✕</button>
                            </div>
                        ) : (
                            <div className="chatPlaceholder">
                                <div className="heart-wrapper">
                                    <div className="heart"></div>
                                </div>
                                <p>Sistemul este pregătit. Scrie direct sau atașează o imagine folosind iconița din colț.</p>
                            </div>
                        )}
                    </div>

                   
                    <form onSubmit={handleSend} className="chatInputWrapper">
                        <label className="attachFileBtn" title="Încarcă screenshot">
                            📷
                            <input type="file" onChange={handleFileChange} accept="image/*" style={{ display: 'none' }} />
                        </label>
                        
                        <input 
                            type="text" 
                            placeholder={preview ? "Adaugă o descriere imaginii sau trimite..." : "Scrie mesajul prietenului tău aici..."} 
                            value={rawText}
                            onChange={(e) => setRawText(e.target.value)}
                            className="chatTextField"
                            disabled={loading}
                        />

                        <button type="submit" className="chatSendBtn" disabled={loading || (!rawText.trim() && !file)}>
                            {loading ? <div className="btnSpinner"></div> : "➔"}
                        </button>
                    </form>
                </div>

                <div className="resultCard">
                    <div className="cardHeader">
                        <h3>Diagnostic AI</h3>
                        {result?.cached && <span className="cacheBadge">Rezultat Securizat (Locked)</span>}
                    </div>

                    {result ? (
                        <div className="resultContent">
                            <div className="scoreSection">
                                <div className="scoreRing">
                                    <span className="scoreNumber">{result.score}%</span>
                                    <span className="scoreLabel">Scor Risc</span>
                                </div>
                                <div className="categoryTag">{result.category}</div>
                            </div>

                            <div className="diagnosticGrid">
                                <div className={`diagItem ${result.indicators?.is_adio ? 'active-red' : ''}`}>
                                    📌 Adio / Finalitate
                                </div>
                                <div className={`diagItem ${result.indicators?.is_iminent ? 'active-red' : ''}`}>
                                    ⏰ Plan Iminent
                                </div>
                                <div className={`diagItem ${result.indicators?.is_depresie ? 'active-orange' : ''}`}>
                                    👤 Depresie Clinică
                                </div>
                                <div className={`diagItem ${result.indicators?.is_stres ? 'active-purple' : ''}`}>
                                    ⚡ Stres Cotidian
                                </div>
                                <div className={`diagItem ${result.indicators?.is_umor ? 'active-blue' : ''}`}>
                                    🎭 Umor / Sarcasm
                                </div>
                            </div>

                            <div className="analysisBox">
                                <div className="feedbackArea">
                                    <p className="aiFeedback">"{result.feedback}"</p>
                                </div>
                                <div className="extractedTextArea">
                                    <strong>Conținut procesat:</strong>
                                    <p>{result.text_ocr || result.text_raw}</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="emptyResult">
                            <div className="pulse-circle"></div>
                            <p>Așteptare date din conversație...</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}