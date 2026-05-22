import { useState, useEffect } from "react";

export default function DashboardStats({ chatId, onClose }) {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (chatId) {
            fetchStats();
        }
    }, [chatId]);

    const fetchStats = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/get-chat-stats/${chatId}?period=all`);
            const data = await response.json();
            setStats(data);
        } catch (error) {
            console.error("Eroare:", error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="dashboard-overlay">
                <div className="dashboard-card">
                    <div className="dashboard-loading">Încărcare...</div>
                </div>
            </div>
        );
    }

    if (!stats) return null;

    return (
        <div className="dashboard-overlay" onClick={onClose}>
            <div className="dashboard-card" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="dashboard-header">
                    <div>
                        <h2>Statistici</h2>
                        <p className="dashboard-subtitle">{stats.nume_persoana}</p>
                    </div>
                    <button className="dashboard-close" onClick={onClose}>×</button>
                </div>

                {/* Grid 2x2 */}
                <div className="dashboard-grid">
                    <div className="stat-block">
                        <span className="stat-label">Scor mediu</span>
                        <span className="stat-number">{stats.scor_mediu}%</span>
                        {stats.trend !== 0 && (
                            <span className={`stat-trend ${stats.trend > 0 ? 'trend-up' : 'trend-down'}`}>
                                {stats.trend > 0 ? '↑' : '↓'} {Math.abs(stats.trend)}%
                            </span>
                        )}
                    </div>

                    <div className="stat-block">
                        <span className="stat-label">Total analize</span>
                        <span className="stat-number">{stats.total_analize}</span>
                        <span className="stat-hint">{stats.mesaje_critice} critice</span>
                    </div>

                    <div className="stat-block">
                        <span className="stat-label">Categorie principală</span>
                        <span className="stat-number small">{stats.categorie_principala || "N/A"}</span>
                        <span className="stat-hint">{stats.categorie_procent}% din analize</span>
                    </div>

                    <div className="stat-block">
                        <span className="stat-label">Perioadă</span>
                        <span className="stat-number small">{stats.prima_analiza?.split(' ')[0] || "N/A"}</span>
                        <span className="stat-hint">→ {stats.ultima_analiza?.split(' ')[0] || "N/A"}</span>
                    </div>
                </div>

                {/* Distribuție categorii - doar bara simplă */}
                {stats.categorii && Object.keys(stats.categorii).length > 0 && (
                    <div className="dashboard-section">
                        <div className="section-header">Distribuție categorii</div>
                        <div className="category-list">
                            {Object.entries(stats.categorii).map(([cat, count]) => {
                                const total = stats.total_analize;
                                const percent = Math.round((count / total) * 100);
                                let barColor = "#565f89";
                                if (cat === "Urgență") barColor = "#f7768e";
                                else if (cat === "Risc Ridicat") barColor = "#ff9f43";
                                else if (cat === "Stres") barColor = "#7aa2f7";
                                else if (cat === "Neutru") barColor = "#73daca";
                                
                                return (
                                    <div key={cat} className="category-item">
                                        <div className="category-info">
                                            <span>{cat}</span>
                                            <span>{percent}%</span>
                                        </div>
                                        <div className="category-bar">
                                            <div className="category-fill" style={{ width: `${percent}%`, background: barColor }}></div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Top indicatori */}
                {stats.top_indicatori && stats.top_indicatori.length > 0 && (
                    <div className="dashboard-section">
                        <div className="section-header">Indicatori frecvenți</div>
                        <div className="indicator-list">
                            {stats.top_indicatori.map((ind, idx) => (
                                <div key={idx} className="indicator-pill">
                                    {ind.nume}
                                    <span>{ind.count}x</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Ultimele mesaje critice */}
                {stats.mesaje_critice_lista && stats.mesaje_critice_lista.length > 0 && (
                    <div className="dashboard-section">
                        <div className="section-header">Ultimele alerte</div>
                        <div className="alert-list">
                            {stats.mesaje_critice_lista.slice(0, 3).map((msg, idx) => (
                                <div key={idx} className="alert-item">
                                    <span className="alert-score">{msg.score}%</span>
                                    <span className="alert-text">{msg.text?.substring(0, 60)}...</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}