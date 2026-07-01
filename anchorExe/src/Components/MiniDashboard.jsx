import { useState, useEffect, useRef } from "react";
import DashboardStats from "./DashboardStats";
import "../css_files/dashboard.css";

// Heart Rhythm Pulse SVG Icon
const HeartPulseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="heart-rhythm-svg">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
  </svg>
);

const CloseIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" x2="6" y1="6" y2="18" />
    <line x1="6" x2="18" y1="6" y2="18" />
  </svg>
);

export default function MiniDashboard() {
  const [isOpen, setIsOpen] = useState(false);
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState("");
  const [chatStats, setChatStats] = useState(null);
  const [multimodalStats, setMultimodalStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showFullStats, setShowFullStats] = useState(false);

  const selectedChatIdRef = useRef(selectedChatId);
  const lastFetchedStatsIdRef = useRef(null);

  useEffect(() => {
    selectedChatIdRef.current = selectedChatId;
  }, [selectedChatId]);

  // Fetch chats on mount and register custom listeners
  useEffect(() => {
    fetchChats();
    
    const handleUpdate = () => {
      fetchChats();
      // Instantly refresh stats on update events
      const activeId = localStorage.getItem("activeChatId");
      const currentSelected = selectedChatIdRef.current;
      const targetId = activeId || currentSelected;
      if (targetId) {
        fetchStats(targetId);
      }
    };

    window.addEventListener("chats-updated", handleUpdate);
    return () => window.removeEventListener("chats-updated", handleUpdate);
  }, []);

  // Re-fetch chats if open toggles to true
  useEffect(() => {
    if (isOpen) {
      fetchChats();
    }
  }, [isOpen]);

  // Fetch stats when selectedChatId changes
  useEffect(() => {
    if (selectedChatId) {
      if (lastFetchedStatsIdRef.current !== selectedChatId) {
        fetchStats(selectedChatId);
      }
    } else {
      setChatStats(null);
      setMultimodalStats(null);
      lastFetchedStatsIdRef.current = null;
    }
  }, [selectedChatId]);

  const fetchChats = async () => {
    try {
      const response = await fetch("http://localhost:5000/get-chats");
      const data = await response.json();
      setChats(data);
      
      const activeId = localStorage.getItem("activeChatId");
      const currentSelected = selectedChatIdRef.current;
      if (activeId && data.some(c => c.id === Number(activeId))) {
        setSelectedChatId(activeId);
      } else if (data.length > 0 && !currentSelected) {
        setSelectedChatId(data[0].id);
      }
    } catch (error) {
      console.error("Error fetching chats in mini dashboard:", error);
    }
  };

  const fetchStats = async (chatId) => {
    lastFetchedStatsIdRef.current = chatId;
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/get-chat-stats/${chatId}?period=all`);
      const textData = await response.json();
      setChatStats(textData);

      const mResponse = await fetch(`http://localhost:5000/get-multimodal-stats/${chatId}`);
      if (mResponse.ok) {
        const mData = await mResponse.json();
        if (mData.status === "success") {
          setMultimodalStats(mData.stats);
        }
      }
    } catch (error) {
      console.error("Error fetching stats in mini dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (e) => {
    if (e) {
      e.preventDefault();
      e.stopPropagation();
    }
    if (!selectedChatId) return;
    if (!window.confirm("Sigur dorești să ștergi acest subiect și toate datele sale definitiv?")) return;
    
    setIsDeleting(true);
    const idToDelete = Number(selectedChatId);
    
    try {
      const response = await fetch(`http://localhost:5000/delete-chat/${idToDelete}`, {
        method: "DELETE"
      });
      if (response.ok) {
        const remainingChats = chats.filter(c => c.id !== idToDelete);
        setChats(remainingChats);
        
        const nextId = remainingChats.length > 0 ? remainingChats[0].id : "";
        setSelectedChatId(nextId);
        localStorage.setItem("activeChatId", nextId);
        
        window.dispatchEvent(new Event("chats-updated"));
      } else {
        alert("Eroare la ștergerea subiectului de pe server.");
      }
    } catch (error) {
      console.error("Error deleting user:", error);
    } finally {
      setIsDeleting(false);
    }
  };

  const selectedChat = chats.find((c) => c.id === Number(selectedChatId));
  const evaluationType =
    selectedChat?.tip_detectie === "apropiat" || chatStats?.tip_detectie === "apropiat"
      ? "Apropiat"
      : "Personală";

  const getScoreColor = (score) => {
    if (score >= 70) return "var(--error)";
    if (score >= 40) return "var(--warning)";
    return "var(--success)";
  };

  // Mini-gauge variables
  const miniRadius = 36;
  const miniCircumference = 2 * Math.PI * miniRadius;
  const scoreVal = multimodalStats ? Math.round(multimodalStats.combined_average) : 0;
  const miniStrokeDashoffset = miniCircumference - (scoreVal / 100) * miniCircumference;
  const activeColor = getScoreColor(scoreVal);

  return (
    <div className="mini-dashboard-container">
      {/* Pulse Heart-Rhythm Trigger */}
      {!isOpen && (
        <button
          className="mini-dashboard-trigger"
          onClick={() => setIsOpen(true)}
          title="Senzor Multimodal Rapid"
        >
          <HeartPulseIcon />
          <span className="trigger-pulse"></span>
        </button>
      )}

      {/* Futuristic Holographic Panel */}
      {isOpen && (
        <div className="mini-dashboard-card premium-holo-card">
          
          {/* Header */}
          <div className="mini-dashboard-header">
            <div className="header-title-group">
              <span className="mini-ping-node"></span>
              <h3>Senzor Biometric</h3>
              <span className="live-badge">LIVE</span>
            </div>
            <button className="mini-dashboard-close-btn" onClick={() => setIsOpen(false)}>
              <CloseIcon />
            </button>
          </div>

          <div className="mini-dashboard-body">
            
            {/* Subject Selector & Direct Delete */}
            <div className="selector-group-row">
              <div className="select-wrapper">
                <label htmlFor="mini-chat-select">Subiect în Monitorizare</label>
                <select
                  id="mini-chat-select"
                  value={selectedChatId}
                  onChange={(e) => {
                    const newId = e.target.value;
                    setSelectedChatId(newId);
                    localStorage.setItem("activeChatId", newId);
                    window.dispatchEvent(new Event("chats-updated"));
                  }}
                  className="mini-dashboard-select"
                >
                  {chats.length === 0 ? (
                    <option value="">Niciun subiect</option>
                  ) : (
                    chats.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.nume_persoana}
                      </option>
                    ))
                  )}
                </select>
              </div>
              
              {selectedChatId && (
                <>
                  <button
                    type="button"
                    onClick={() => setShowFullStats(true)}
                    className="mini-open-stats-btn"
                    title="Vizualizează analize detaliate și grafice evoluție"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" x2="18" y1="20" y2="10" />
                      <line x1="12" x2="12" y1="20" y2="4" />
                      <line x1="6" x2="6" y1="20" y2="14" />
                    </svg>
                  </button>

                  <button
                    type="button"
                    onClick={handleDeleteUser}
                    className="mini-delete-trash-btn"
                    title="Șterge definitiv subiectul"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6" />
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                    </svg>
                  </button>
                </>
              )}
            </div>

            {loading ? (
              <div className="mini-dashboard-loading-spinner">
                <div className="spinner"></div>
                <span>Scanare date...</span>
              </div>
            ) : selectedChatId && multimodalStats ? (
              <div className={`stats-display-area animate-fade-in ${isDeleting ? "deleting-active" : ""}`}>
                
                {/* ID Header Details */}
                <div className="meta-details-row">
                  <span className="subject-id-tag">ID: <span>#{selectedChatId}</span></span>
                  <span className={`evaluation-badge type-${evaluationType.toLowerCase()}`}>
                    {evaluationType}
                  </span>
                </div>

                {/* Circular Mini Gauge Block */}
                <div 
                  className="multimodal-score-block mini-holo-gauge-card clickable-gauge-card"
                  onClick={() => setShowFullStats(true)}
                  title="Click pentru grafic evoluție și diagnostic complet"
                  style={{ cursor: "pointer" }}
                >
                  <span className="score-title">Agregat Multimodal</span>
                  
                  <div className="mini-gauge-svg-wrapper">
                    <svg className="mini-radial-svg" width="90" height="90" viewBox="0 0 90 90">
                      <defs>
                        <filter id="neon-glow-mini" x="-25%" y="-25%" width="150%" height="150%">
                          <feGaussianBlur stdDeviation="3.5" result="blur" />
                          <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                          </feMerge>
                        </filter>
                      </defs>
                      <circle className="mini-gauge-track" cx="45" cy="45" r={miniRadius} strokeWidth="5.5" />
                      <circle 
                        className="mini-gauge-progress" 
                        cx="45" 
                        cy="45" 
                        r={miniRadius} 
                        strokeWidth="5.5" 
                        stroke={activeColor}
                        strokeDasharray={miniCircumference}
                        strokeDashoffset={miniStrokeDashoffset}
                        filter="url(#neon-glow-mini)"
                        strokeLinecap="round"
                        transform="rotate(-90 45 45)"
                      />
                    </svg>
                    <div className="mini-gauge-text-overlay">
                      <span className="mini-gauge-score-pct" style={{ color: activeColor }}>
                        {scoreVal}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* Modular Status Meters */}
                <div className="individual-metrics-grid">
                  <div className="metric-box box-text" onClick={() => setShowFullStats(true)} style={{ cursor: "pointer" }} title="Click pentru grafice detaliate">
                    <span className="metric-label">Text</span>
                    <span className="metric-value" style={{ color: "#7aa2f7" }}>{multimodalStats.text_average}%</span>
                  </div>
                  <div className="metric-box box-voice" onClick={() => setShowFullStats(true)} style={{ cursor: "pointer" }} title="Click pentru grafice detaliate">
                    <span className="metric-label">Voce</span>
                    <span className="metric-value" style={{ color: "#73daca" }}>{multimodalStats.voice_average}%</span>
                  </div>
                  <div className="metric-box box-face" onClick={() => setShowFullStats(true)} style={{ cursor: "pointer" }} title="Click pentru grafice detaliate">
                    <span className="metric-label">Față</span>
                    <span className="metric-value" style={{ color: "#bb9af7" }}>{multimodalStats.face_average}%</span>
                  </div>
                </div>

                {/* Recommendation Block */}
                <div className="recommendation-block" style={{ borderLeftColor: activeColor }}>
                  <span className="rec-title" style={{ color: activeColor }}>Status</span>
                  <p className="rec-text">{multimodalStats.recommendation}</p>
                </div>

                {/* Evolution & Details Button */}
                <button
                  type="button"
                  onClick={() => setShowFullStats(true)}
                  className="mini-view-details-btn"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M3 3v18h18" />
                    <path d="m18.7 8-5.1 5.2-2.8-2.7L7 14.3" />
                  </svg>
                  Diagramă & Grafice Evoluție
                </button>

              </div>
            ) : (
              <div className="no-stats-placeholder">
                <p>Niciun raport disponibil. Adăugați mesaje, înregistrări vocale sau imagini de mimică pentru a genera senzori.</p>
              </div>
            )}

          </div>
        </div>
      )}

      {/* Render the full stats modal overlay if open */}
      {showFullStats && selectedChatId && (
        <DashboardStats
          chatId={Number(selectedChatId)}
          onClose={() => setShowFullStats(false)}
        />
      )}
    </div>
  );
}
