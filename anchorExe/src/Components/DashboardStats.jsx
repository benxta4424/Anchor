import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import "../css_files/dashboard.css";

export default function DashboardStats({ chatId, onClose }) {
    const [stats, setStats] = useState(null);
    const [multimodalStats, setMultimodalStats] = useState(null);
    const [textHistory, setTextHistory] = useState([]);
    const [voiceHistory, setVoiceHistory] = useState([]);
    const [faceHistory, setFaceHistory] = useState([]);
    const [advancedInsights, setAdvancedInsights] = useState(null);
    const [activeTab, setActiveTab] = useState("overview"); // overview, evolution, spectrum, alerts
    const [loading, setLoading] = useState(true);
    const [hoveredPoint, setHoveredPoint] = useState(null);

    useEffect(() => {
        if (chatId) {
            fetchStats();
        }
    }, [chatId]);

    useEffect(() => {
        const originalOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => {
            document.body.style.overflow = originalOverflow;
        };
    }, []);

    const fetchStats = async () => {
        setLoading(true);
        try {
            // Fetch text-chat statistics
            const response = await fetch(`http://localhost:5000/get-chat-stats/${chatId}?period=all`);
            const data = await response.json();
            setStats(data);

            // Fetch combined multimodal stats (Text + Voice + Face)
            const mResponse = await fetch(`http://localhost:5000/get-multimodal-stats/${chatId}`);
            if (mResponse.ok) {
                const mData = await mResponse.json();
                if (mData.status === "success") {
                    setMultimodalStats(mData.stats);
                }
            }

            // Fetch text scores timeline
            try {
                const textHistoryRes = await fetch(`http://localhost:5000/get-chat-scores/${chatId}`);
                if (textHistoryRes.ok) {
                    const textData = await textHistoryRes.json();
                    setTextHistory(textData);
                }
            } catch (err) {
                console.error("Eroare istoric text:", err);
            }

            // Fetch voice timeline
            try {
                const voiceHistoryRes = await fetch(`http://localhost:5000/get-voice-history/${chatId}`);
                if (voiceHistoryRes.ok) {
                    const vData = await voiceHistoryRes.json();
                    if (vData.status === "success") {
                        setVoiceHistory(vData.history || []);
                    }
                }
            } catch (err) {
                console.error("Eroare istoric voce:", err);
            }

            // Fetch face timeline
            try {
                const faceHistoryRes = await fetch(`http://localhost:5000/get-face-history/${chatId}`);
                if (faceHistoryRes.ok) {
                    const fData = await faceHistoryRes.json();
                    if (fData.status === "success") {
                        setFaceHistory(fData.history || []);
                    }
                }
            } catch (err) {
                console.error("Eroare istoric fata:", err);
            }

            // Fetch advanced insights
            try {
                const advRes = await fetch(`http://localhost:5000/advanced-insights/${chatId}`);
                if (advRes.ok) {
                    const advData = await advRes.json();
                    setAdvancedInsights(advData);
                }
            } catch (err) {
                console.error("Eroare insights avansate:", err);
            }
        } catch (error) {
            console.error("Eroare la preluarea statisticilor:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return createPortal(
            <div className="dashboard-overlay">
                <div className="premium-glass-loader-card">
                    <div className="loader-container">
                        <div className="loading-orbit"></div>
                        <span>Securizare canal biometric...</span>
                    </div>
                </div>
            </div>,
            document.body
        );
    }

    if (!stats) return null;

    // Biometric data preprocessing
    const textScore = stats.scor_mediu || 0;
    const voiceScore = multimodalStats ? Math.round(multimodalStats.voice_average) : 0;
    const faceScore = multimodalStats ? Math.round(multimodalStats.face_average) : 0;
    const combinedScore = multimodalStats ? Math.round(multimodalStats.combined_average) : textScore;

    // Determine colors
    let glowColor = "var(--success)"; // safe green
    let glowColorName = "success";
    if (combinedScore >= 70) {
        glowColor = "var(--error)"; // severe red
        glowColorName = "critical";
    } else if (combinedScore >= 40) {
        glowColor = "var(--warning)"; // moderate yellow
        glowColorName = "warning";
    }

    // Radial Gauge mathematics
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (combinedScore / 100) * circumference;

    // Timeline Chart parameters
    const paddingLeft = 55;
    const paddingRight = 30;
    const paddingTop = 30;
    const paddingBottom = 45;
    const width = 760;
    const height = 280;
    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;
    const yGridValues = [0, 25, 50, 75, 100];

    const buildTimelineData = () => {
        const combined = [];
        
        (textHistory || []).forEach(item => {
            if (item.score !== null && item.score !== undefined) {
                combined.push({
                    timestamp: new Date(item.data.replace(' ', 'T')).getTime(),
                    label: item.data,
                    type: 'text',
                    score: item.score
                });
            }
        });

        (voiceHistory || []).forEach(item => {
            if (item.voice_score !== null && item.voice_score !== undefined) {
                combined.push({
                    timestamp: new Date(item.timestamp.replace(' ', 'T')).getTime(),
                    label: item.timestamp,
                    type: 'voice',
                    score: item.voice_score
                });
            }
        });

        (faceHistory || []).forEach(item => {
            if (item.depression_score !== null && item.depression_score !== undefined) {
                combined.push({
                    timestamp: new Date(item.timestamp.replace(' ', 'T')).getTime(),
                    label: item.timestamp,
                    type: 'face',
                    score: item.depression_score
                });
            }
        });

        // Sort chronologically
        combined.sort((a, b) => a.timestamp - b.timestamp);

        // Group by unique timestamps to align on X axis
        const uniqueTimestamps = Array.from(new Set(combined.map(item => item.timestamp))).sort((a, b) => a - b);

        const seriesData = uniqueTimestamps.map(ts => {
            const dateObj = new Date(ts);
            const dateLabel = dateObj.toLocaleDateString("ro-RO", { month: "short", day: "numeric" }) + " " + dateObj.toLocaleTimeString("ro-RO", { hour: "2-digit", minute: "2-digit" });
            
            const textPoint = combined.find(item => item.timestamp === ts && item.type === 'text');
            const voicePoint = combined.find(item => item.timestamp === ts && item.type === 'voice');
            const facePoint = combined.find(item => item.timestamp === ts && item.type === 'face');
            
            return {
                timestamp: ts,
                label: dateLabel,
                text: textPoint ? textPoint.score : null,
                voice: voicePoint ? voicePoint.score : null,
                face: facePoint ? facePoint.score : null
            };
        });

        return seriesData.slice(-12); // limit to last 12 points for visual beauty
    };

    const timelineData = buildTimelineData();

    const drawModalityLine = (series, key, color) => {
        const points = series
            .map((d, idx) => {
                if (d[key] === null || d[key] === undefined) return null;
                const x = series.length > 1 
                    ? paddingLeft + (idx / (series.length - 1)) * chartWidth 
                    : paddingLeft + chartWidth / 2;
                const y = paddingTop + chartHeight - (d[key] / 100) * chartHeight;
                return { x, y, val: d[key], label: d.label };
            })
            .filter(p => p !== null);

        if (points.length === 0) return null;

        // Generate line path
        let dAttr = `M ${points[0].x} ${points[0].y}`;
        for (let i = 1; i < points.length; i++) {
            dAttr += ` L ${points[i].x} ${points[i].y}`;
        }

        return (
            <g key={key}>
                {/* Glow layer */}
                {points.length > 1 && (
                    <path 
                        d={dAttr} 
                        fill="none" 
                        stroke={color} 
                        strokeWidth="5" 
                        opacity="0.25" 
                        filter="url(#neon-glow-chart)" 
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                )}
                {/* Core line */}
                {points.length > 1 && (
                    <path 
                        d={dAttr} 
                        fill="none" 
                        stroke={color} 
                        strokeWidth="2.5" 
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                )}
                {/* Interactive dots */}
                {points.map((p, pIdx) => (
                    <g 
                        key={pIdx}
                        onMouseEnter={() => setHoveredPoint({ x: p.x, y: p.y, val: p.val, label: p.label, type: key, color })}
                        onMouseLeave={() => setHoveredPoint(null)}
                    >
                        <circle 
                            cx={p.x} 
                            cy={p.y} 
                            r="7" 
                            fill={color} 
                            opacity="0.3" 
                            filter="url(#neon-glow-chart)"
                            style={{ cursor: "pointer" }}
                        />
                        <circle 
                            cx={p.x} 
                            cy={p.y} 
                            r="4.5" 
                            fill="#0b0d17" 
                            stroke={color} 
                            strokeWidth="2" 
                            style={{ cursor: "pointer" }}
                        />
                    </g>
                ))}
            </g>
        );
    };

    return createPortal(
        <div className="dashboard-overlay" onClick={onClose}>
            <div className="dashboard-card premium-layout animate-fade-in" onClick={(e) => e.stopPropagation()}>
                
                {/* Header Section */}
                <div className="dashboard-header">
                    <div className="header-info">
                        <div className="heart-wrapper small-heart">
                            <div className="heart active-heart"></div>
                        </div>
                        <div>
                            <h2>Raport Evoluție Emoțională</h2>
                            <p className="dashboard-subtitle">
                                {multimodalStats && multimodalStats.tip_detectie === 'mine' ? 'Analiză pentru: ' : 'Subiect: '}
                                <span>{multimodalStats && multimodalStats.tip_detectie === 'mine' ? 'Tine' : (stats?.nume_persoana || '')}</span>
                            </p>
                        </div>
                    </div>

                    {/* Navigation Tabs */}
                    <div className="dashboard-tabs">
                        <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
                            🔬 Sinteză
                        </button>
                        <button className={`tab-btn ${activeTab === 'evolution' ? 'active' : ''}`} onClick={() => setActiveTab('evolution')}>
                            📈 Traiectorie
                        </button>
                        <button className={`tab-btn ${activeTab === 'spectrum' ? 'active' : ''}`} onClick={() => setActiveTab('spectrum')}>
                            🧠 Spectru
                        </button>
                        <button className={`tab-btn ${activeTab === 'alerts' ? 'active' : ''}`} onClick={() => setActiveTab('alerts')}>
                            🚨 Alerte
                        </button>
                    </div>

                    <button className="dashboard-close" onClick={onClose} aria-label="Închide">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                             <line x1="18" x2="6" y1="6" y2="18"/>
                             <line x1="6" x2="18" y1="6" y2="18"/>
                        </svg>
                    </button>
                </div>

                {/* Dashboard Tab Content */}
                <div className="dashboard-tab-container">
                    
                    {/* Tab 1: Overview (Sinteză) */}
                    {activeTab === 'overview' && (
                        <div className="dashboard-body-grid animate-fade-in">
                            {/* Left Column: Multimodal Diagnostics */}
                            <div className="dashboard-col-left">
                                
                                {/* Circular Biometric Risk Ring */}
                                <div className="biometric-gauge-card">
                                    <span className="card-tag">Senzor Agregat</span>
                                    <div className="gauge-wrapper">
                                        <svg className="radial-gauge" width="180" height="180" viewBox="0 0 180 180">
                                            <defs>
                                                <filter id="neon-glow-main" x="-30%" y="-30%" width="160%" height="160%">
                                                    <feGaussianBlur stdDeviation="8" result="blur" />
                                                    <feMerge>
                                                        <feMergeNode in="blur" />
                                                        <feMergeNode in="SourceGraphic" />
                                                    </feMerge>
                                                </filter>
                                            </defs>
                                            
                                            {/* Track Ring */}
                                            <circle className="gauge-track" cx="90" cy="90" r={radius} strokeWidth="10" />
                                            
                                            {/* Progress Ring */}
                                            <circle 
                                                className="gauge-progress" 
                                                cx="90" 
                                                cy="90" 
                                                r={radius} 
                                                strokeWidth="10" 
                                                stroke={glowColor}
                                                strokeDasharray={circumference}
                                                strokeDashoffset={strokeDashoffset}
                                                filter="url(#neon-glow-main)"
                                                strokeLinecap="round"
                                            />
                                            
                                            {/* Cyber Grid Lines */}
                                            <circle className="gauge-decor" cx="90" cy="90" r={radius - 12} strokeWidth="1" strokeDasharray="3, 5" />
                                        </svg>
                                        
                                        <div className="gauge-center">
                                            <span className="gauge-score" style={{ color: glowColor, textShadow: `0 0 15px ${glowColor}` }}>
                                                {combinedScore}%
                                            </span>
                                            <span className="gauge-label">Risc Agregat</span>
                                        </div>
                                    </div>

                                    <div className="gauge-recommendation" style={{ borderColor: `${glowColor}30` }}>
                                        <span className={`rec-badge ${glowColorName}`} style={{ color: glowColor, border: `1px solid ${glowColor}` }}>
                                            {combinedScore >= 70 ? "🚨 Risc Sever" : combinedScore >= 40 ? "⚠️ Risc Moderat" : "✅ Risc Scăzut"}
                                        </span>
                                        <p className="rec-text">{multimodalStats ? multimodalStats.recommendation : "Analiză clinică în curs"}</p>
                                    </div>
                                </div>

                                {/* Modality Sensors Feed */}
                                <div className="modality-feeds-card">
                                    <span className="card-tag">Modul Biometric</span>
                                    <div className="feed-items">
                                        {/* Text Modality */}
                                        <div className="feed-item">
                                            <div className="feed-meta">
                                                <div className="feed-title-group">
                                                    <span className="feed-dot text"></span>
                                                    <span>Analiză Semantică (Text)</span>
                                                </div>
                                                <span className="feed-score">{textScore}%</span>
                                            </div>
                                            <div className="feed-progress-bar">
                                                <div className="feed-progress-fill text" style={{ width: `${textScore}%` }}></div>
                                            </div>
                                        </div>

                                        {/* Voice Modality */}
                                        <div className="feed-item">
                                            <div className="feed-meta">
                                                <div className="feed-title-group">
                                                    <span className="feed-dot voice"></span>
                                                    <span>Prosodie Vocală (Voce)</span>
                                                </div>
                                                <span className="feed-score">{voiceScore}%</span>
                                            </div>
                                            <div className="feed-progress-bar">
                                                <div className="feed-progress-fill voice" style={{ width: `${voiceScore}%` }}></div>
                                            </div>
                                        </div>

                                        {/* Face Modality */}
                                        <div className="feed-item">
                                            <div className="feed-meta">
                                                <div className="feed-title-group">
                                                    <span className="feed-dot face"></span>
                                                    <span>Micro-Expresii (Față)</span>
                                                </div>
                                                <span className="feed-score">{faceScore}%</span>
                                            </div>
                                            <div className="feed-progress-bar">
                                                <div className="feed-progress-fill face" style={{ width: `${faceScore}%` }}></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                            </div>

                            {/* Right Column: Detailed Clinical Insights */}
                            <div className="dashboard-col-right">
                                
                                {/* Biometric Grid Cards */}
                                <div className="mini-stats-grid">
                                    <div className="glass-stat-block">
                                        <span className="block-label">Risc Mediu Semantic</span>
                                        <span className="block-val">{stats.scor_mediu}%</span>
                                        {stats.trend !== 0 && (
                                            <span className={`block-trend-pill ${stats.trend > 0 ? "bad" : "good"}`}>
                                                {stats.trend > 0 ? "▲" : "▼"} {Math.abs(stats.trend)}% trend
                                            </span>
                                        )}
                                    </div>
                                    
                                    <div className="glass-stat-block">
                                        <span className="block-label">Evaluări Totale</span>
                                        <span className="block-val">{stats.total_analize}</span>
                                        <span className="block-subtext">{stats.mesaje_critice} alerte cordon roșu</span>
                                    </div>

                                    <div className="glass-stat-block">
                                        <span className="block-label">Diagnostic Text</span>
                                        <span className="block-val small-font">{stats.categorie_principala || "N/A"}</span>
                                        <span className="block-subtext">{stats.categorie_procent}% prevalență</span>
                                    </div>

                                    <div className="glass-stat-block">
                                        <span className="block-label">Fereastră Timp</span>
                                        <span className="block-val small-font date-font">{stats.prima_analiza?.split(' ')[0] || "N/A"}</span>
                                        <span className="block-subtext">→ {stats.ultima_analiza?.split(' ')[0] || "N/A"}</span>
                                    </div>
                                </div>

                                <div className="glass-stat-block full-width-recommendation" style={{ minHeight: "auto", display: "block" }}>
                                    <span className="block-label" style={{ display: "block", marginBottom: "8px" }}>Concluzie Diagnostică</span>
                                    <p className="rec-text" style={{ margin: 0 }}>
                                        Pe baza analizei clinice a datelor textuale, prosodice și mimice, pacientul înregistrează un risc agregat de <strong>{combinedScore}%</strong>. Se recomandă monitorizarea continuă conform ghidurilor clinice.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Tab 2: Evolution (Traiectorie) */}
                    {activeTab === 'evolution' && (
                        <div className="tab-evolution-content animate-fade-in">
                            <div className="evolution-chart-card">
                                <span className="card-tag">Grafic Evoluție Multimodală (Ultimul Istoric)</span>
                                
                                {timelineData.length === 0 ? (
                                    <div className="empty-chart-state">
                                        <p>Date cronologice insuficiente pentru randarea traiectoriei emoționale.</p>
                                        <span className="empty-chart-sub">Sunt necesare mesaje analizate, înregistrări vocale sau scanări faciale.</span>
                                    </div>
                                ) : (
                                    <div className="svg-chart-container" style={{ position: "relative", width: "100%", overflowX: "auto" }}>
                                        <svg className="svg-chart-element" viewBox={`0 0 ${width} ${height}`} width="100%" height={height}>
                                            <defs>
                                                <filter id="neon-glow-chart" x="-20%" y="-20%" width="140%" height="140%">
                                                    <feGaussianBlur stdDeviation="5" result="blur" />
                                                    <feMerge>
                                                        <feMergeNode in="blur" />
                                                        <feMergeNode in="SourceGraphic" />
                                                    </feMerge>
                                                </filter>
                                            </defs>
                                            
                                            {/* Draw Y Grid Lines */}
                                            {yGridValues.map(val => {
                                                const y = paddingTop + chartHeight - (val / 100) * chartHeight;
                                                return (
                                                    <g key={val} className="chart-grid-line-group">
                                                        <line 
                                                            x1={paddingLeft} 
                                                            y1={y} 
                                                            x2={paddingLeft + chartWidth} 
                                                            y2={y} 
                                                            stroke="rgba(255, 255, 255, 0.05)" 
                                                            strokeWidth="1"
                                                            strokeDasharray="4, 4"
                                                        />
                                                        <text 
                                                            x={paddingLeft - 12} 
                                                            y={y + 3} 
                                                            fill="rgba(255, 255, 255, 0.35)" 
                                                            fontSize="9" 
                                                            textAnchor="end"
                                                            fontFamily="monospace"
                                                        >
                                                            {val}%
                                                        </text>
                                                    </g>
                                                );
                                            })}
                                            
                                            {/* Draw X axis line */}
                                            <line 
                                                x1={paddingLeft} 
                                                y1={paddingTop + chartHeight} 
                                                x2={paddingLeft + chartWidth} 
                                                y2={paddingTop + chartHeight} 
                                                stroke="rgba(255, 255, 255, 0.1)" 
                                                strokeWidth="1"
                                            />
                                            
                                            {/* Draw X Labels */}
                                            {timelineData.map((d, idx) => {
                                                const x = timelineData.length > 1 
                                                    ? paddingLeft + (idx / (timelineData.length - 1)) * chartWidth 
                                                    : paddingLeft + chartWidth / 2;
                                                return (
                                                    <g key={idx}>
                                                        <line 
                                                            x1={x} 
                                                            y1={paddingTop} 
                                                            x2={x} 
                                                            y2={paddingTop + chartHeight} 
                                                            stroke="rgba(255, 255, 255, 0.02)" 
                                                            strokeWidth="1"
                                                        />
                                                        <text 
                                                            x={x} 
                                                            y={paddingTop + chartHeight + 20} 
                                                            fill="rgba(255, 255, 255, 0.4)" 
                                                            fontSize="8" 
                                                            textAnchor="middle"
                                                            transform={`rotate(-15, ${x}, ${paddingTop + chartHeight + 20})`}
                                                        >
                                                            {d.label.split(' ')[0]}
                                                        </text>
                                                    </g>
                                                );
                                            })}
                                            
                                            {/* Draw lines for each modality */}
                                            {drawModalityLine(timelineData, 'text', '#7aa2f7')}
                                            {drawModalityLine(timelineData, 'voice', '#73daca')}
                                            {drawModalityLine(timelineData, 'face', '#bb9af7')}
                                        </svg>
                                        
                                        {/* Tooltip Overlay */}
                                        {hoveredPoint && (
                                            <div 
                                                className="chart-tooltip" 
                                                style={{ 
                                                    position: "absolute", 
                                                    left: `${(hoveredPoint.x / width) * 100}%`, 
                                                    top: `${(hoveredPoint.y / height) * 100}%`,
                                                    transform: "translate(-50%, -115%)",
                                                    background: "rgba(11, 13, 23, 0.96)",
                                                    border: `1px solid ${hoveredPoint.color}`,
                                                    borderRadius: "6px",
                                                    padding: "6px 10px",
                                                    color: "#c0caf5",
                                                    fontSize: "11px",
                                                    pointerEvents: "none",
                                                    zIndex: 10,
                                                    boxShadow: `0 8px 24px rgba(0, 0, 0, 0.7), 0 0 10px ${hoveredPoint.color}35`,
                                                    fontFamily: "var(--font-body)",
                                                    whiteSpace: "nowrap"
                                                }}
                                            >
                                                <div style={{ fontWeight: "700", textTransform: "uppercase", fontSize: "9px", letterSpacing: "0.5px", color: hoveredPoint.color, marginBottom: "2px" }}>
                                                    {hoveredPoint.type === 'text' ? 'Analiză Text' : hoveredPoint.type === 'voice' ? 'Prosodie Voce' : 'Expresie Față'}
                                                </div>
                                                <div style={{ color: "#fff", fontSize: "12px" }}>Risc: <strong style={{ color: hoveredPoint.color }}>{hoveredPoint.val}%</strong></div>
                                                <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "9px", marginTop: "2px" }}>{hoveredPoint.label}</div>
                                            </div>
                                        )}
                                    </div>
                                )}
                                
                                {/* Chart Legend */}
                                <div className="chart-legend-row">
                                    <div className="legend-item"><span className="legend-line-dot text"></span> Analiză Semantică</div>
                                    <div className="legend-item"><span className="legend-line-dot voice"></span> Prosodie Voce</div>
                                    <div className="legend-item"><span className="legend-line-dot face"></span> Expresie Față</div>
                                </div>
                            </div>

                            {/* Trajectory Stats Grid */}
                            <div className="trajectory-stats-grid">
                                <div className="glass-stat-block">
                                    <span className="block-label">Evoluție Emoțională</span>
                                    <span className="block-val small-font" style={{ color: "var(--primary)" }}>
                                        {advancedInsights?.emotional_trajectory || (stats.trend > 0 ? "📈 Deteriorare" : stats.trend < 0 ? "📉 Îmbunătățire" : "⚖️ Constantă")}
                                    </span>
                                    <span className="block-subtext">Interpretare pe baza traiectoriei recente</span>
                                </div>
                                <div className="glass-stat-block">
                                    <span className="block-label">Extreme Înregistrate (Min / Max)</span>
                                    <div className="extremes-row">
                                        <span className="extreme-item max" style={{ color: "var(--error)" }}>
                                            Max: {timelineData.length > 0 ? Math.max(...timelineData.map(d => Math.max(d.text || 0, d.voice || 0, d.face || 0))) : 0}%
                                        </span>
                                        <span className="extreme-item min" style={{ color: "var(--success)" }}>
                                            Min: {timelineData.length > 0 ? Math.min(...timelineData.map(d => Math.min(d.text !== null ? d.text : 100, d.voice !== null ? d.voice : 100, d.face !== null ? d.face : 100))) : 0}%
                                        </span>
                                    </div>
                                    <span className="block-subtext">Vârfuri de risc vs. minime</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Tab 3: Spectrum (Spectru) */}
                    {activeTab === 'spectrum' && (
                        <div className="tab-spectrum-content animate-fade-in">
                            <div className="spectrum-layout-row">
                                
                                {/* Left Side: Emotion breakdown & Markers */}
                                <div className="spectrum-side-left">
                                    {stats.categorii && Object.keys(stats.categorii).length > 0 && (
                                        <div className="spectrum-card">
                                            <span className="card-tag">Spectru Emoțional Înregistrat</span>
                                            <div className="spectrum-bars">
                                                {Object.entries(stats.categorii).map(([cat, count]) => {
                                                    const total = stats.total_analize;
                                                    const percent = Math.round((count / total) * 100);
                                                    let barClass = "normal";
                                                    if (cat === "Urgență") barClass = "critical";
                                                    else if (cat === "Risc Ridicat") barClass = "high";
                                                    else if (cat === "Stres") barClass = "warning";
                                                    else if (cat === "Neutru") barClass = "success";
                                                    
                                                    return (
                                                        <div key={cat} className="spectrum-bar-item">
                                                            <div className="bar-meta">
                                                                <span>{cat}</span>
                                                                <span>{percent}%</span>
                                                            </div>
                                                            <div className="bar-track">
                                                                <div className={`bar-fill-indicator ${barClass}`} style={{ width: `${percent}%` }}></div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </div>
                                    )}

                                    {stats.top_indicatori && stats.top_indicatori.length > 0 && (
                                        <div className="indicators-card">
                                            <span className="card-tag">Markeri Lingvistici Corelați</span>
                                            <div className="indicators-flex-list">
                                                {stats.top_indicatori.map((ind, idx) => (
                                                    <div key={idx} className="indicator-tech-pill">
                                                        <span className="pill-dot"></span>
                                                        <span className="pill-name">{ind.nume}</span>
                                                        <span className="pill-badge">{ind.count}x</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Right Side: Cognitive indicators */}
                                <div className="spectrum-side-right">
                                    <div className="advanced-insights-card">
                                        <span className="card-tag">Indicatori Cognitivi Avansați</span>
                                        <div className="insights-checklist">
                                            <div className="insight-item">
                                                <span className="insight-lbl">Flat Affect (Mascare Psihică)</span>
                                                <span className={`insight-val ${faceScore > 45 && textScore < 30 ? "warning-text" : "success-text"}`}>
                                                    {faceScore > 45 && textScore < 30 ? "⚠️ Risc Detectat (Exprimare mimică plată)" : "✅ Coerență Expresie / Limbaj"}
                                                </span>
                                            </div>
                                            <div className="insight-item">
                                                <span className="insight-lbl">Marcaje de Sarcasm / Disonanță</span>
                                                <span className={`insight-val ${advancedInsights?.sarcasm_detected ? "warning-text" : "success-text"}`}>
                                                    {advancedInsights?.sarcasm_detected ? "⚠️ Disonanță Semantico-Contextuală" : "✅ Lipsă (Comunicare Directă)"}
                                                </span>
                                            </div>
                                            <div className="insight-item">
                                                <span className="insight-lbl">Stare Dominantă Text</span>
                                                <span className="insight-val" style={{ color: "var(--primary)" }}>
                                                    {stats.categorie_principala || "N/A"}
                                                </span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Advanced recommendations block */}
                                    <div className="recommendation-block" style={{ marginTop: "14px" }}>
                                        <span className="rec-title">Insight Clinic Personalizat</span>
                                        <p className="rec-text">
                                            {advancedInsights?.clinical_recommendation || "Analiza semantică indică o evoluție clinică stabilă. Monitorizați disonanțele dintre prosodia vocii și stările declarate textual în cadrul chat-ului."}
                                        </p>
                                    </div>
                                </div>

                            </div>
                        </div>
                    )}

                    {/* Tab 4: Alerts (Alerte) */}
                    {activeTab === 'alerts' && (
                        <div className="tab-alerts-content animate-fade-in">
                            {/* Real-time Hazard Alert Log */}
                            <div className="hazard-log-card" style={{ marginBottom: "16px" }}>
                                <span className="card-tag">Hazard Log (Alerte Roșii & Evenimente Critice)</span>
                                {stats.mesaje_critice_lista && stats.mesaje_critice_lista.length > 0 ? (
                                    <div className="hazard-list">
                                        {stats.mesaje_critice_lista.map((msg, idx) => (
                                            <div key={idx} className="hazard-item">
                                                <div className="hazard-header-meta">
                                                    <span className="hazard-ping"></span>
                                                    <span className="hazard-score">{msg.score}% Risc</span>
                                                    <span className="hazard-date" style={{ fontSize: "10px", color: "var(--text-muted)", marginLeft: "auto" }}>{msg.data}</span>
                                                </div>
                                                <p className="hazard-text">"{msg.text}"</p>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="no-hazards-placeholder" style={{ padding: "30px 0", color: "var(--text-faint)", fontSize: "12px", textAlign: "center" }}>
                                        Niciun incident critic înregistrat (&gt;80% risc clinic).
                                    </div>
                                )}
                            </div>

                            {/* Support contacts */}
                            <div className="support-emergency-card" style={{ background: "rgba(247, 118, 142, 0.05)", border: "1px solid rgba(247, 118, 142, 0.15)", padding: "16px", borderRadius: "12px" }}>
                                <span className="card-tag" style={{ color: "var(--error)", marginBottom: "8px", display: "inline-block" }}>📞 LINII TELEFONICE DE SPRIJIN & ASISTENȚĂ MEDICALĂ</span>
                                <p className="rec-text" style={{ fontSize: "12px", margin: "0 0 14px 0", lineHeight: "1.4" }}>
                                    Dacă pacientul prezintă gânduri negre sau comportamente de risc iminent, nu ezitați să apelați serviciile specializate de consiliere și intervenție rapidă:
                                </p>
                                <div className="severeHelplinesGrid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                    <a href="tel:0800801200" className="severeHelplineLink" style={{ display: "flex", flexDirection: "column", padding: "12px", background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: "8px", textDecoration: "none", color: "inherit", transition: "all 0.2s ease" }}>
                                        <span style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase" }}>Asociația Speranța (Antisuicid)</span>
                                        <strong style={{ fontSize: "14px", color: "#f7768e", marginTop: "4px" }}>0800 801 200</strong>
                                    </a>
                                    <a href="tel:112" className="severeHelplineLink" style={{ display: "flex", flexDirection: "column", padding: "12px", background: "rgba(0,0,0,0.25)", border: "1px solid rgba(255,255,255,0.06)", borderRadius: "8px", textDecoration: "none", color: "inherit", transition: "all 0.2s ease" }}>
                                        <span style={{ fontSize: "9.5px", color: "var(--text-muted)", textTransform: "uppercase" }}>Serviciul Național Unic</span>
                                        <strong style={{ fontSize: "14px", color: "#f7768e", marginTop: "4px" }}>112</strong>
                                    </a>
                                </div>
                            </div>
                        </div>
                    )}

                </div>

            </div>
        </div>,
        document.body
    );
}