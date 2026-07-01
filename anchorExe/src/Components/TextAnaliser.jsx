import { useState, useEffect, useRef } from "react";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    LineElement,
    PointElement,
    LinearScale,
    CategoryScale,
    Tooltip as ChartTooltip,
    Filler,
} from "chart.js";
import ClinicalChart from "./ClinicalChart";
import EmergencyPopup from "./EmergencyPopup";
import DashboardStats from "./DashboardStats";

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, ChartTooltip, Filler);

// SVG Icons
const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="18" y1="20" y2="10" />
    <line x1="12" x2="12" y1="20" y2="4" />
    <line x1="6" x2="6" y1="20" y2="14" />
  </svg>
);

const DashboardIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M3 3v18h18" />
    <path d="m18.7 8-5.1 5.2-2.8-2.7L7 14.3" />
  </svg>
);

const AttachIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
  </svg>
);

const CrossIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <line x1="18" x2="6" y1="6" y2="18" />
    <line x1="6" x2="18" y1="6" y2="18" />
  </svg>
);

const PrintIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <polyline points="6 9 6 2 18 2 18 9" />
    <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
    <rect x="6" y="14" width="12" height="8" rx="1" />
  </svg>
);

export default function TextAnaliser() {
    const [chats, setChats] = useState([]);
    const [activeChat, setActiveChat] = useState(null);
    const [showNewChatModal, setShowNewChatModal] = useState(false);
    const [newPersonName, setNewPersonName] = useState("");
    const [tipDetectie, setTipDetectie] = useState("mine");

    const [rawText, setRawText] = useState("");
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [chatMessages, setChatMessages] = useState([]);
    const [lastScore, setLastScore] = useState(null);

    const [showChartModal, setShowChartModal] = useState(false);  // ✅ corect
    const [chartData, setChartData] = useState([]);

    const [showEmergencyPopup, setShowEmergencyPopup] = useState(false);
    const [criticalScore, setCriticalScore] = useState(null);

    const [showDashboard, setShowDashboard] = useState(false);
    const [deletingId, setDeletingId] = useState(null);
    const [latestDiagnosis, setLatestDiagnosis] = useState(null);
    const [showDiagnosticPanel, setShowDiagnosticPanel] = useState(false);
    const [checklist, setChecklist] = useState([]);


    const messagesEndRef = useRef(null);
    const activeChatRef = useRef(activeChat);
    const prevActiveChatIdRef = useRef(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        activeChatRef.current = activeChat;
    }, [activeChat]);

    useEffect(() => {
        fetchChats();
        const handleChatsUpdated = () => {
            fetchChats();
        };
        window.addEventListener("chats-updated", handleChatsUpdated);
        return () => window.removeEventListener("chats-updated", handleChatsUpdated);
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [chatMessages]);

    useEffect(() => {
        if (activeChat) {
            const idChanged = prevActiveChatIdRef.current !== activeChat.id;
            prevActiveChatIdRef.current = activeChat.id;

            localStorage.setItem("activeChatId", activeChat.id);
            
            if (idChanged) {
                fetchChatMessages(activeChat.id);
                fetchChartData(activeChat.id);
                fetchLatestDiagnosis(activeChat.id);
                setLastScore(null);
                // Notify other components (like MiniDashboard) of selection switch
                window.dispatchEvent(new Event("chats-updated"));
            }
        } else {
            const wasActive = prevActiveChatIdRef.current !== null;
            prevActiveChatIdRef.current = null;

            localStorage.removeItem("activeChatId");
            setChatMessages([]);
            setChartData([]);
            setLatestDiagnosis(null);
            setChecklist([]);
            setLastScore(null);
            
            if (wasActive) {
                window.dispatchEvent(new Event("chats-updated"));
            }
        }
    }, [activeChat]);

    const fetchChats = async () => {
        try {
            const response = await fetch("http://localhost:5000/get-chats");
            const data = await response.json();
            setChats(data);
            
            // Sync activeChat with activeChatId in localStorage
            const storedId = localStorage.getItem("activeChatId");
            const currentActive = activeChatRef.current;
            if (storedId) {
                const storedChat = data.find(c => c.id === Number(storedId));
                if (storedChat && currentActive?.id !== storedChat.id) {
                    setActiveChat(storedChat);
                }
            } else if (data.length > 0 && !currentActive) {
                setActiveChat(data[0]);
            }
        } catch (error) { console.error(error); }
    };

    const fetchChatMessages = async (chatId) => {
        try {
            const response = await fetch(`http://localhost:5000/get-chat-messages/${chatId}`);
            const data = await response.json();
            setChatMessages(data);
        } catch (error) { console.error(error); }
    };

    const fetchChartData = async (chatId) => {
        try {
            const response = await fetch(`http://localhost:5000/get-chat-scores/${chatId}`);
            const data = await response.json();
            const filtered = data.filter(d => d.score !== null && d.score !== undefined);
            setChartData(filtered);
        } catch (error) { console.error(error); }
    };

    const fetchLatestDiagnosis = async (chatId) => {
        try {
            const response = await fetch(`http://localhost:5000/get-latest-diagnosis/${chatId}`);
            const data = await response.json();
            if (data.status === "success") {
                setLatestDiagnosis(data);
                setLastScore({ score: data.score, category: data.category });
                initializeChecklist(data.score);
            } else {
                setLatestDiagnosis(null);
                setLastScore(null);
                setChecklist([]);
            }
        } catch (error) {
            console.error("Error loading latest diagnosis:", error);
        }
    };

    const initializeChecklist = (score) => {
        if (score === null || score === undefined) {
            setChecklist([]);
            return;
        }
        let tasks = [];
        if (score >= 70) {
            tasks = [
                { id: 1, text: "Contactează o persoană de încredere pentru suport", completed: false },
                { id: 2, text: "Practică respirația controlată (4-7-8) timp de 3 minute", completed: false },
                { id: 3, text: "Redu stimulii vizuali și ecranele pentru restul zilei", completed: false },
                { id: 4, text: "Amână orice decizie majoră sau de impact", completed: false }
            ];
        } else if (score >= 35) {
            tasks = [
                { id: 1, text: "Fă o plimbare de 15 minute în aer liber", completed: false },
                { id: 2, text: "Notează în jurnal gândurile care te apasă", completed: false },
                { id: 3, text: "Ascultă o piesă muzicală relaxantă", completed: false },
                { id: 4, text: "Ia o pauză scurtă de deconectare", completed: false }
            ];
        } else {
            tasks = [
                { id: 1, text: "Exprimă recunoștință pentru un lucru bun de azi", completed: false },
                { id: 2, text: "Menține hidratarea și fă mișcare ușoară", completed: false },
                { id: 3, text: "Stabilește o activitate plăcută pentru mâine", completed: false }
            ];
        }
        setChecklist(tasks);
    };

    const handleToggleChecklist = (id) => {
        setChecklist(prev => prev.map(item => 
            item.id === id ? { ...item, completed: !item.completed } : item
        ));
    };

    const getScoreGaugeColor = (score) => {
        if (score >= 70) return "#f7768e"; // red
        if (score >= 40) return "#e0af68"; // yellow
        return "#73ddca"; // green
    };

    const getCategoryBadgeClass = (score) => {
        if (score >= 70) return "badge-red";
        if (score >= 40) return "badge-yellow";
        return "badge-green";
    };

    const getMiniChartConfig = () => {
        if (!chartData || chartData.length === 0) return { labels: [], datasets: [] };
        
        const labels = chartData.map((d, i) => {
            const date = new Date(d.data);
            if (isNaN(date.getTime())) return `${i + 1}`;
            return `${date.getDate()}/${date.getMonth() + 1}`;
        });
        const scores = chartData.map(d => d.score);
        const pointColors = scores.map(s => {
            if (s >= 80) return "#f7768e";
            if (s >= 55) return "#ff9f43";
            if (s >= 30) return "#7aa2f7";
            return "#73daca";
        });
        return {
            labels,
            datasets: [{
                label: "Scor Risc",
                data: scores,
                borderColor: "#7aa2f7",
                borderWidth: 2,
                pointBackgroundColor: pointColors,
                pointBorderColor: "#0b0c16",
                pointBorderWidth: 1.5,
                pointRadius: 4.5,
                tension: 0.35,
                fill: true,
                backgroundColor: "rgba(122, 162, 247, 0.04)",
            }]
        };
    };

    const miniChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
            legend: { display: false }, 
            tooltip: { 
                enabled: true,
                backgroundColor: "#0d0f18",
                titleColor: "#7aa2f7",
                bodyColor: "#c0caf5",
                borderColor: "#1f2335",
                borderWidth: 1,
                padding: 8
            } 
        },
        scales: {
            y: {
                min: 0,
                max: 100,
                ticks: { color: "#565f89", font: { size: 9 }, stepSize: 25 },
                grid: { color: "rgba(255,255,255,0.03)" }
            },
            x: {
                ticks: { color: "#565f89", font: { size: 9 } },
                grid: { display: false }
            }
        }
    };

    // Monitorizare scor critic pentru popup
    useEffect(() => {
        if (lastScore && lastScore.score >= 70) {
            setCriticalScore(lastScore.score);
            setShowEmergencyPopup(true);
        }
    }, [lastScore]);

    const handleCreateChat = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch("http://localhost:5000/create-chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    nume: newPersonName.trim(),
                    tip_detectie: tipDetectie
                })
            });
            const newChat = await response.json();
            setChats((prev) => [newChat, ...prev]);
            setActiveChat(newChat);
            setNewPersonName("");
            setTipDetectie("mine");
            setShowNewChatModal(false);
        } catch (error) { alert("Eroare la crearea sesiunii."); }
    };

    const handleDeleteChat = async (chatId, e) => {
        e.stopPropagation();
        if (!window.confirm("Sigur dorești să ștergi această sesiune?")) return;
        setDeletingId(chatId);
        
        try {
            const response = await fetch(`http://localhost:5000/delete-chat/${chatId}`, { method: "DELETE" });
            if (response.ok) {
                const updatedChats = chats.filter(c => c.id !== chatId);
                setChats(updatedChats);
                
                if (activeChat?.id === chatId) {
                    const nextActive = updatedChats.length > 0 ? updatedChats[0] : null;
                    setActiveChat(nextActive);
                    if (nextActive) {
                        localStorage.setItem("activeChatId", nextActive.id);
                    } else {
                        localStorage.removeItem("activeChatId");
                    }
                }
                // Notify other components after successful server delete
                window.dispatchEvent(new Event("chats-updated"));
            } else {
                alert("Eroare la ștergerea de pe server.");
            }
        } catch (error) {
            console.error("Eroare la ștergerea sesiunii:", error);
        } finally {
            setDeletingId(null);
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
        const currentFile = file;

        setChatMessages((prev) => [...prev, { sender: "user", text: currentText, image: currentPreview }]);
        setLoading(true);
        setRawText("");
        setFile(null);
        setPreview(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }

        const formData = new FormData();
        formData.append("chatId", activeChat.id);
        if (currentText) formData.append("rawText", currentText);
        if (currentFile) formData.append("image", currentFile);
        formData.append("trigger_diagnosis", "false");

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
                indicators: data.indicators,
                trend: data.trend_statistic,
            }]);
            const newScore = { score: data.score, category: data.category };
            setLastScore(newScore);

            // refresh grafic după trimitere
            fetchChartData(activeChat.id);
            
            // Dispatch update event to sync stats globally
            window.dispatchEvent(new Event("chats-updated"));
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleTriggerDiagnosis = async () => {
        if (!activeChat) return;
        setLoading(true);
        const formData = new FormData();
        formData.append("chatId", activeChat.id);
        formData.append("trigger_diagnosis", "true");
        formData.append("rawText", "Generează diagnoză pe baza conversației");

        try {
            const response = await fetch("http://localhost:5000/analyze-text", {
                method: "POST",
                body: formData,
            });
            const data = await response.json();

            setLatestDiagnosis({
                score: data.score,
                category: data.category,
                feedback: data.feedback,
                indicators: data.indicators,
                trajectory: data.emotional_trajectory ? data.emotional_trajectory.trend : "N/A",
                voice_avg: 0,
                face_avg: 0
            });
            initializeChecklist(data.score);
            setShowDiagnosticPanel(true);

            setChatMessages((prev) => [...prev, {
                sender: "system",
                text: `📊 O nouă evaluare clinică a fost generată în panoul lateral (${data.score}% - ${data.category}).`
            }]);

            const newScore = { score: data.score, category: data.category };
            setLastScore(newScore);

            // refresh grafic după trimitere
            fetchChartData(activeChat.id);
            
            // Dispatch update event to sync stats globally
            window.dispatchEvent(new Event("chats-updated"));
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // ─── RENDER ────────────────────────────────────────────────────
    return (
        <div className={`cleanDashboard ${showDiagnosticPanel ? "diagnostic-open" : ""}`}>

            {/* SIDEBAR */}
            <aside className="cleanSidebar">
                <div className="sidebarTopRow">
                    <span>Sesiuni</span>
                    <button onClick={() => setShowNewChatModal(true)} className="cleanAddBtn">+</button>
                </div>
                <div className="cleanList">
                    {chats.map((c) => (
                        <div
                            key={c.id}
                            className={`cleanItem ${activeChat?.id === c.id ? "active" : ""} ${deletingId === c.id ? "deleting" : ""}`}
                            onClick={() => setActiveChat(c)}
                        >
                            <span className="title">{c.nume_persoana}</span>
                            <button
                                className="deleteChatBtn"
                                onClick={(e) => handleDeleteChat(c.id, e)}
                                title="Șterge sesiunea"
                            ><CrossIcon /></button>
                        </div>
                    ))}
                </div>
            </aside>

            {/* ZONA DE CONVERSAȚIE */}
            <main className="cleanChatArea">

                {/* HEADER */}
                <div className="cleanChatHeader">
                    <div className="headerMeta">
                        <h3>{activeChat ? activeChat.nume_persoana : "Selectați un subiect"}</h3>
                    </div>
                    <div className="headerRight">
                        {lastScore && lastScore.score !== null && lastScore.score !== undefined && (
                            <div className="headerScore">
                                Risc: <strong>{lastScore.score}%</strong>
                            </div>
                        )}
                        
                        {activeChat && (
                            <button
                                className={`chartToggleBtn ${showDiagnosticPanel ? "active" : ""}`}
                                onClick={() => setShowDiagnosticPanel(!showDiagnosticPanel)}
                                title="Panou Diagnoză Clinică"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                                </svg>
                            </button>
                        )}
                        
                        {activeChat && chartData.length > 0 && (
                            <button
                                className={`chartToggleBtn ${showChartModal ? "active" : ""}`}
                                onClick={() => setShowChartModal(true)}
                                title="Grafic evoluție">
                                <ChartIcon />
                            </button>
                        )}

                        {activeChat && chartData.length > 0 && (
                            <button
                                className="chartToggleBtn"
                                onClick={() => setShowDashboard(true)}
                                title="Dashboard statistici"
                            >
                                <DashboardIcon />
                            </button>
                        )}

                        {activeChat && (
                            <button
                                className="chartToggleBtn"
                                onClick={() => window.print()}
                                title="Tipărește raport PDF"
                            >
                                <PrintIcon />
                            </button>
                        )}
                    </div>
                </div>

                {/* MESAJE */}
                <div className="cleanChatBody">
                    {chatMessages.length === 0 ? (
                        <div className="cleanEmptyState">
                            <p>Introduceți date text sau capturi de ecran pentru analiză.</p>
                        </div>
                    ) : (
                        chatMessages.map((msg, index) => {
                            if (msg.sender === "system") {
                                return (
                                    <div key={index} className="cleanMsgRow system" style={{ display: "flex", justifyContent: "center", margin: "12px 0", width: "100%" }}>
                                        <div className="systemNotification" style={{
                                            background: "rgba(122, 162, 247, 0.08)",
                                            border: "1px solid rgba(122, 162, 247, 0.2)",
                                            color: "var(--primary)",
                                            fontSize: "12px",
                                            padding: "6px 16px",
                                            borderRadius: "var(--radius-full)",
                                            fontFamily: "var(--font-body)",
                                            fontWeight: "500",
                                            textAlign: "center"
                                        }}>
                                            {msg.text}
                                        </div>
                                    </div>
                                );
                            }

                            if (msg.sender === "ai" && msg.score !== null && msg.score !== undefined) {
                                // Render historic diagnosis as a clickable pill
                                return (
                                    <div key={index} className="cleanMsgRow system" style={{ display: "flex", justifyContent: "center", margin: "12px 0", width: "100%" }}>
                                        <div 
                                            className="systemNotification" 
                                            style={{
                                                background: "rgba(115, 221, 202, 0.08)",
                                                border: "1px solid rgba(115, 221, 202, 0.2)",
                                                color: "var(--success)",
                                                fontSize: "12px",
                                                padding: "6px 16px",
                                                borderRadius: "var(--radius-full)",
                                                fontFamily: "var(--font-body)",
                                                fontWeight: "500",
                                                textAlign: "center",
                                                cursor: "pointer",
                                                transition: "all 0.2s ease"
                                            }}
                                            onClick={() => {
                                                setLatestDiagnosis(prev => ({
                                                    score: msg.score,
                                                    category: msg.category,
                                                    feedback: msg.text,
                                                    indicators: msg.indicators,
                                                    trajectory: msg.trend || "Stabil",
                                                    voice_avg: prev ? prev.voice_avg : 0,
                                                    face_avg: prev ? prev.face_avg : 0
                                                }));
                                                initializeChecklist(msg.score);
                                                setShowDiagnosticPanel(true);
                                                
                                                // Sync with MiniDashboard on click
                                                window.dispatchEvent(new Event("chats-updated"));
                                            }}
                                            title="Click pentru a vizualiza raportul în panoul lateral"
                                        >
                                            📊 Evaluare clinică înregistrată ({msg.score}% - {msg.category}) - Click pentru detalii
                                        </div>
                                    </div>
                                );
                            }

                            return (
                                <div key={index} className={`cleanMsgRow ${msg.sender}`}>
                                    <div className="cleanBubble">
                                        {msg.image && <img src={msg.image} alt="Data snapshot" className="cleanBubbleImg" />}
                                        {msg.text && <p className="msgText">{msg.text}</p>}
                                    </div>
                                </div>
                            );
                        })
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSend} className="cleanConsoleFooter">
                    {preview && (
                        <div className="cleanImagePreview">
                            <img src={preview} alt="Buffer snapshot" />
                            <button type="button" onClick={() => { setFile(null); setPreview(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}><CrossIcon /></button>
                        </div>
                    )}
                    {activeChat && (
                        <div className="consoleActionRow" style={{ display: "flex", justifyContent: "flex-end", marginBottom: "8px" }}>
                            <button
                                type="button"
                                className="triggerDiagnosisBtn"
                                onClick={handleTriggerDiagnosis}
                                disabled={loading}
                                style={{
                                    background: "rgba(122, 162, 247, 0.1)",
                                    border: "1px solid rgba(122, 162, 247, 0.25)",
                                    color: "var(--primary)",
                                    borderRadius: "var(--radius-btn)",
                                    padding: "6px 14px",
                                    fontSize: "12px",
                                    fontWeight: "var(--weight-semibold)",
                                    cursor: "pointer",
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "6px",
                                    transition: "var(--transition-colors)"
                                }}
                            >
                                📊 Generează Diagnoză
                            </button>
                        </div>
                    )}
                    <div className="cleanInputRow">
                        <label className="dnaAttachBtn" title="Atașează o imagine sau captură">
                            <AttachIcon />
                            <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: "none" }} />
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

            {/* INTERACTIVE DIAGNOSTIC WORKSPACE */}
            <aside className={`cleanDiagnosticPanel ${showDiagnosticPanel ? "" : "collapsed"}`}>
                <div className="diagnosticHeader">
                    <h3>Workspace Diagnoză</h3>
                    <button 
                        className="diagnosticHeaderCloseBtn"
                        onClick={() => setShowDiagnosticPanel(false)}
                        title="Închide panoul"
                    >
                        <CrossIcon />
                    </button>
                </div>
                
                {chartData && chartData.length > 0 ? (
                    <div className="diagnosticContent">
                        
                        {latestDiagnosis ? (
                            <>
                                {/* Futuristic Digital Score Dashboard Card */}
                                <div className="clinicalDashboardCard">
                                    <div className="clinicalMainStats">
                                        <div className="clinicalScoreDisplay">
                                            <div className="clinicalLedScore" style={{ color: getScoreGaugeColor(latestDiagnosis.score), textShadow: `0 0 15px ${getScoreGaugeColor(latestDiagnosis.score)}` }}>
                                                {latestDiagnosis.score}%
                                            </div>
                                            <div className="clinicalScoreLabel">RISC ESTIMAT</div>
                                        </div>
                                        
                                        <div className="clinicalMetaDisplay">
                                            <div className={`clinicalStatusBadge ${getCategoryBadgeClass(latestDiagnosis.score)}`}>
                                                <span className="pulseDot" style={{ backgroundColor: getScoreGaugeColor(latestDiagnosis.score), boxShadow: `0 0 8px ${getScoreGaugeColor(latestDiagnosis.score)}` }}></span>
                                                {latestDiagnosis.category}
                                            </div>
                                            
                                            <div className="clinicalTrajectoryPill">
                                                <span className="pillLabel">Traiectorie:</span>
                                                <span className="pillVal">{latestDiagnosis.trajectory || "Stabilă"}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Multimodal progress bars if voice or face metrics exist */}
                                    {(latestDiagnosis.voice_avg > 0 || latestDiagnosis.face_avg > 0) && (
                                        <div className="clinicalMultimodalSection">
                                            <span className="multimodalTitle">INDICATORI BIOMETRICI</span>
                                            <div className="multimodalProgressGrid">
                                                {latestDiagnosis.voice_avg > 0 && (
                                                    <div className="mProgressBarItem">
                                                        <div className="progressBarMeta">
                                                            <span>Prosodie Voce</span>
                                                            <strong>{latestDiagnosis.voice_avg}%</strong>
                                                        </div>
                                                        <div className="progressBarBg">
                                                            <div className="progressBarFill" style={{ width: `${latestDiagnosis.voice_avg}%`, backgroundColor: "var(--primary)" }}></div>
                                                        </div>
                                                    </div>
                                                )}
                                                {latestDiagnosis.face_avg > 0 && (
                                                    <div className="mProgressBarItem">
                                                        <div className="progressBarMeta">
                                                            <span>Micro-Expresii Față</span>
                                                            <strong>{latestDiagnosis.face_avg}%</strong>
                                                        </div>
                                                        <div className="progressBarBg">
                                                            <div className="progressBarFill" style={{ width: `${latestDiagnosis.face_avg}%`, backgroundColor: "var(--accent)" }}></div>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </>
                        ) : (
                            <div className="commentaryText" style={{ textAlign: "center", padding: "16px", borderStyle: "dashed" }}>
                                <p style={{ margin: 0, fontSize: "12px", color: "var(--text-muted)" }}>Nicio diagnoză generată pentru starea curentă.</p>
                                <p style={{ margin: "6px 0 0", fontSize: "10px", color: "var(--text-faint)" }}>
                                    Apasă pe <strong>Generează Diagnoză</strong> în subsol pentru o analiză de context.
                                </p>
                            </div>
                        )}

                        {/* Futuristic Monitoring Evolution Chart Card */}
                        <div className="clinicalChartCard">
                            <div className="clinicalChartHeader">
                                <div className="chartTitleGroup">
                                    <span className="titleDot"></span>
                                    <h4>ISTORIC RISC CLINIC</h4>
                                </div>
                                <span className="chartSubtitle">Evoluție temporală</span>
                            </div>
                            <div className="clinicalChartCanvasWrapper">
                                <Line data={getMiniChartConfig()} options={miniChartOptions} />
                            </div>
                            <div className="clinicalChartLegend">
                                <div className="legendItem"><span className="legendDot critical"></span> Sever (&gt;70%)</div>
                                <div className="legendItem"><span className="legendDot warning"></span> Moderat (30-70%)</div>
                                <div className="legendItem"><span className="legendDot success"></span> Scăzut (&lt;30%)</div>
                            </div>
                        </div>

                        {latestDiagnosis && (
                            <>
                                {/* Detailed Clinical Report */}
                                <div className="diagnosticSection">
                                    <span className="sectionTitle">Evaluare Detaliată Stare de Spirit</span>
                                    <p className="commentaryText">{latestDiagnosis.feedback}</p>
                                </div>

                                {/* Coping Checklist */}
                                {checklist.length > 0 && (
                                    <div className="diagnosticSection">
                                        <span className="sectionTitle">Plan de Coping Personalizat</span>
                                        <div className="checklistWrapper">
                                            <div className="checklistHeader">
                                                <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>Sarcini recomandate</span>
                                                <span className="checklistProgress">
                                                    {checklist.filter(t => t.completed).length}/{checklist.length}
                                                </span>
                                            </div>
                                            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                                                {checklist.map(task => (
                                                    <div 
                                                        key={task.id} 
                                                        className={`checklistItem ${task.completed ? "completed" : ""}`}
                                                        onClick={() => handleToggleChecklist(task.id)}
                                                    >
                                                        <div className="checklistCheckbox">
                                                            {task.completed && (
                                                                <svg className="checkIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="10" height="10">
                                                                    <polyline points="20 6 9 17 4 12" />
                                                                </svg>
                                                            )}
                                                        </div>
                                                        <span>{task.text}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {/* Emergency resources if severe */}
                                {latestDiagnosis.score >= 70 && (
                                    <div className="severeRiskCard animate-fade-in">
                                        <div className="severeRiskHeader">
                                            <span>⚠️ SUPORT ȘI AJUTOR DE URGENȚĂ</span>
                                        </div>
                                        <p>Nivelul de risc identificat este ridicat. Te rugăm să nu treci prin asta singur. Contactează sprijin de specialitate imediat:</p>
                                        <div className="severeHelplinesGrid">
                                            <a href="tel:0800801200" className="severeHelplineLink">
                                                <span>Telefonul Speranței (Antisuicid)</span>
                                                <strong>0800 801 200</strong>
                                            </a>
                                            <a href="tel:112" className="severeHelplineLink">
                                                <span>Serviciul de Urgență Național</span>
                                                <strong>112</strong>
                                            </a>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                ) : (
                    <div className="emptyDiagnosticState">
                        <svg className="emptyDiagnosticIcon" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                            <polyline points="14 2 14 8 20 8" />
                            <line x1="16" y1="13" x2="8" y2="13" />
                            <line x1="16" y1="17" x2="8" y2="17" />
                            <line x1="10" y1="9" x2="8" y2="9" />
                        </svg>
                        <p>Nicio diagnoză generată pentru această sesiune.</p>
                        <p style={{ fontSize: "11px", marginTop: "4px" }}>
                            Folosiți butonul <strong>Generează Diagnoză</strong> pentru a analiza conversația.
                        </p>
                    </div>
                )}
            </aside>

            {showChartModal && (
                <ClinicalChart 
                    chartData={chartData} 
                    onClose={() => setShowChartModal(false)}
                />
            )}

            {showDashboard && (
                <DashboardStats 
                    chatId={activeChat?.id} 
                    onClose={() => setShowDashboard(false)}
                />
            )}

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
                                required
                            />
                            <div className="modalRadioGroup" style={{ marginBottom: "16px", display: "flex", flexDirection: "column", gap: "8px" }}>
                                <label style={{ fontSize: "10px", color: "var(--text-muted)", fontWeight: "600", textTransform: "uppercase", letterSpacing: "1px" }}>Tip Detecție</label>
                                <div style={{ display: "flex", gap: "16px" }}>
                                    <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", cursor: "pointer", color: "var(--text)" }}>
                                        <input
                                            type="radio"
                                            name="tipDetectie"
                                            value="mine"
                                            checked={tipDetectie === "mine"}
                                            onChange={() => setTipDetectie("mine")}
                                            style={{ accentColor: "var(--primary)" }}
                                        />
                                        Pentru mine
                                    </label>
                                    <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", cursor: "pointer", color: "var(--text)" }}>
                                        <input
                                            type="radio"
                                            name="tipDetectie"
                                            value="apropiat"
                                            checked={tipDetectie === "apropiat"}
                                            onChange={() => setTipDetectie("apropiat")}
                                            style={{ accentColor: "var(--primary)" }}
                                        />
                                        Pentru un apropiat
                                    </label>
                                </div>
                            </div>
                            <div className="cleanModalActions">
                                <button type="button" onClick={() => { setShowNewChatModal(false); setNewPersonName(""); setTipDetectie("mine"); }}>Anulează</button>
                                <button type="submit" className="cleanConfirm">Creează</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* POPUP URGENȚĂ */}
            {showEmergencyPopup && (
                <EmergencyPopup 
                    score={criticalScore} 
                    onClose={() => setShowEmergencyPopup(false)} 
                />
            )}
        </div>
    );
}