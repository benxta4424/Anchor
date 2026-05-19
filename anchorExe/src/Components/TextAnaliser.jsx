// deci ca sa imi fie mai usor, o sa incerc sa fac un script de pyuthon care face text recognition din poza si mi l trimite ca si text aici ca sa nu incarc AI ul prea mukt
// deci eu o sa primesc SS cu textul unui prieten si scriptul o sa scoata textul din poza ca sa nu trebuiasca sa o faca AI ul
// dupa ce scoate scriptul, o sa trimit in backend API ul AI ului mesajul in sine si o sa l pun sa detecteze asa, pare mnai usor sincer
import { useState, useEffect, useRef } from "react";


export default function TextAnaliser() {
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [showNewChatModal, setShowNewChatModal] = useState(false);
    const [newPersonName, setNewPersonName] = useState("");

    const [rawText, setRawText] = useState("");
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [chatMessages, setChatMessages] = useState([]);
    const [lastScore, setLastScore] = useState(null);

    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchChats();
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatMessages]);

    useEffect(() => {
        if (activeChat) {
            fetchChatMessages(activeChat.id);
            setLastScore(null);
        } else {
            setChatMessages([]);
            setLastScore(null);
        }
    }, [activeChat]);

    const fetchChats = async () => {
        try {
            const response = await fetch("http://localhost:5000/get-chats");
            const data = await response.json();
            setChats(data);
            if (data.length > 0 && !activeChat) setActiveChat(data[0]);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchChatMessages = async (chatId) => {
        try {
            const response = await fetch(`http://localhost:5000/get-chat-messages/${chatId}`);
            const data = await response.json();
            setChatMessages(data);
        } catch (error) {
            console.error(error);
        }
    };

    const handleCreateChat = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://localhost:5000/create-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nume: newPersonName.trim() })
            });
            const newChat = await response.json();
            setChats((prev) => [newChat, ...prev]);
            setActiveChat(newChat);
            setNewPersonName("");
            setShowNewChatModal(false);
        } catch (error) {
            alert("Eroare la crearea sesiunii.");
        }
    };

    // FUNCȚIA NOUĂ PENTRU ȘTERGEREA CHAT-ULUI
    const handleDeleteChat = async (chatId, e) => {
        e.stopPropagation(); // Previne selectarea chat-ului când apeși pe ștergere
        if (!window.confirm("Sigur dorești să ștergi această sesiune?")) return;

        try {
            const response = await fetch(`http://localhost:5000/delete-chat/${chatId}`, {
                method: "DELETE"
            });
            if (response.ok) {
                const updatedChats = chats.filter(c => c.id !== chatId);
                setChats(updatedChats);
                if (activeChat?.id === chatId) {
                    setActiveChat(updatedChats.length > 0 ? updatedChats[0] : null);
                }
            } else {
                alert("Eroare la ștergerea de pe server.");
            }
        } catch (error) {
            console.error("Eroare:", error);
        }
    };

    const handleFileChange = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreview(URL.createObjectURL(selected));
        }
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!activeChat || (!rawText.trim() && !file)) return;

        const currentText = rawText.trim();
        const currentPreview = preview;

        setChatMessages((prev) => [...prev, { sender: "user", text: currentText, image: currentPreview }]);
        setLoading(true);
        setRawText("");
        setFile(null);
        setPreview(null);

        const formData = new FormData();
        formData.append("chatId", activeChat.id);
        if (currentText) formData.append("rawText", currentText);
        if (file) formData.append("image", file);

        try {
            const response = await fetch("http://localhost:5000/analyze-text", {
                method: "POST",
                body: formData,
            });
            const data = await response.json();

            setChatMessages((prev) => [...prev, {
                sender: "ai",
                text: data.feedback,
                score: data.score,
                category: data.category,
                indicators: data.indicators
            }]);
            setLastScore({ score: data.score, category: data.category });
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="cleanDashboard">
            
            {/* SIDEBAR ULTRA-SIMPLU */}
            <aside className="cleanSidebar">
                <div className="sidebarTopRow">
                    <span>Sesiuni</span>
                    <button onClick={() => setShowNewChatModal(true)} className="cleanAddBtn">+</button>
                </div>
                <div className="cleanList">
                    {chats.map((c) => (
                        <div 
                            key={c.id} 
                            className={`cleanItem ${activeChat?.id === c.id ? "active" : ""}`}
                            onClick={() => setActiveChat(c)}
                        >
                            <span className="title">{c.nume_persoana}</span>
                            {/* Butonul de ștergere */}
                            <button 
                                className="deleteChatBtn" 
                                onClick={(e) => handleDeleteChat(c.id, e)}
                                title="Șterge sesiunea"
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            </aside>

            {/* ZONA DE CONVERSAȚIE */}
            <main className="cleanChatArea">
                <div className="cleanChatHeader">
                    <div className="headerMeta">
                        <h3>{activeChat ? activeChat.nume_persoana : "Selectați un subiect"}</h3>
                    </div>
                    {lastScore && (
                        <div className="headerScore">
                            Risc: <strong>{lastScore.score}%</strong>
                        </div>
                    )}
                </div>

                <div className="cleanChatBody">
                    {chatMessages.length === 0 ? (
                        <div className="cleanEmptyState">
                            <p>Introduceți date text sau capturi de ecran pentru analiză.</p>
                        </div>
                    ) : (
                        chatMessages.map((msg, index) => (
                            <div key={index} className={`cleanMsgRow ${msg.sender}`}>
                                <div className="cleanBubble">
                                    {msg.image && <img src={msg.image} alt="Data snapshot" className="cleanBubbleImg" />}
                                    {msg.text && <p className="msgText">{msg.text}</p>}
                                    
                                    {msg.sender === "ai" && (
                                        <div className="diagnosticMetadata">
                                            <span className="scoreLabel">{msg.category} ({msg.score}%)</span>
                                            {msg.indicators && (
                                                <div className="flagsContainer">
                                                    {msg.indicators.is_adio && <span className="cleanFlag status-critical">Adio</span>}
                                                    {msg.indicators.is_iminent && <span className="cleanFlag status-critical">Plan Iminent</span>}
                                                    {msg.indicators.is_depresie && <span className="cleanFlag status-warning">Depresie</span>}
                                                    {msg.indicators.is_stres && <span className="cleanFlag status-info">Stres</span>}
                                                    {msg.indicators.is_umor && <span className="cleanFlag status-neutral">Umor</span>}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* ZONA DE INPUT */}
                <form onSubmit={handleSend} className="cleanConsoleFooter">
                    {preview && (
                        <div className="cleanImagePreview">
                            <img src={preview} alt="Buffer snapshot" />
                            <button type="button" onClick={() => setFile(null) || setPreview(null)}>✕</button>
                        </div>
                    )}
                    <div className="cleanInputRow">
                        <label className="dnaAttachBtn">
                            🧬
                            <input type="file" onChange={handleFileChange} accept="image/*" style={{ display: "none" }} />
                        </label>
                        <input 
                            type="text" 
                            placeholder="Scrie un mesaj..."
                            value={rawText}
                            onChange={(e) => setRawText(e.target.value)}
                            disabled={loading || !activeChat}
                            className="cleanInputField"
                        />
                        <button type="submit" className="cleanSendBtn" disabled={loading || !activeChat || (!rawText.trim() && !file)}>
                            {loading ? <div className="cleanSpinner"></div> : "Trimite"}
                        </button>
                    </div>
                </form>
            </main>

            {/* MODAL MODAL PENTRU ADAUGARE */}
            {showNewChatModal && (
                <div className="cleanModalOverlay">
                    <div className="cleanModal">
                        <h4>Adăugare Subiect</h4>
                        <form onSubmit={handleCreateChat}>
                            <input 
                                type="text" 
                                placeholder="Nume subiect" 
                                value={newPersonName}
                                onChange={(e) => setNewPersonName(e.target.value)}
                                className="cleanModalInput"
                                autoFocus
                            />
                            <div className="cleanModalActions">
                                <button type="button" onClick={() => setShowNewChatModal(false)}>Anulează</button>
                                <button type="submit" className="cleanConfirm">Creează</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

        </div>
    );
}