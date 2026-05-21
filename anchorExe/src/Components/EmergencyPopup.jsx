import React, { useEffect, useCallback } from "react";

const EmergencyPopup = ({ score, onClose }) => {
    // Previne scroll-ul body când popup-ul e deschis
    useEffect(() => {
        const originalOverflow = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        
        return () => {
            document.body.style.overflow = originalOverflow;
        };
    }, []);

    // Handler pentru închidere cu ESC
    const handleKeyDown = useCallback((e) => {
        if (e.key === "Escape") {
            onClose();
        }
    }, [onClose]);

    useEffect(() => {
        window.addEventListener("keydown", handleKeyDown);
        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };
    }, [handleKeyDown]);

    // Handler pentru click pe overlay
    const handleOverlayClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    // Numere de urgență
    const emergencyContacts = [
        { label: "Antisuicid (Alianța Română)", value: "0800 801 200", tel: "0800801200" },
        { label: "Linia Națională Antisuicid", value: "116 123", tel: "116123" },
        { label: "Salvare / Ambulanță", value: "112", tel: "112" },
        { label: "TelVerde Abuz Copii", value: "119", tel: "119" }
    ];

    const handleCall = (phoneNumber) => {
        window.location.href = `tel:${phoneNumber}`;
    };

    return (
        <div 
            className="emergency-popup-overlay" 
            onClick={handleOverlayClick}
            role="dialog"
            aria-modal="true"
            aria-labelledby="emergency-title"
        >
            <div className="emergency-popup">
                <div className="emergency-icon">⚠️🚨</div>
                <h2 id="emergency-title">Intervenție Urgentă Necesară</h2>
                <div className="emergency-score">
                    Scor risc critic: {score}%
                </div>
                <p>
                    Ai nevoie de ajutor chiar acum. Nu ești singur/ă. 
                    Sună la unul dintre numerele de mai jos. 
                    Oamenii de acolo sunt pregătiți să te asculte și să te sprijine.
                </p>
                
                <div className="emergency-numbers">
                    {emergencyContacts.map((contact, idx) => (
                        <div key={idx} className="emergency-number-card">
                            <span className="number-label">{contact.label}</span>
                            <a 
                                href={`tel:${contact.tel}`}
                                className="number-value"
                                onClick={(e) => {
                                    e.preventDefault();
                                    handleCall(contact.tel);
                                }}
                            >
                                {contact.value}
                            </a>
                        </div>
                    ))}
                </div>

                <div className="emergency-buttons">
                    <a 
                        href="tel:112" 
                        className="emergency-call-btn primary"
                        onClick={(e) => {
                            e.preventDefault();
                            handleCall("112");
                        }}
                    >
                        🚑 Sună 112
                    </a>
                    <button 
                        className="emergency-call-btn secondary"
                        onClick={() => handleCall("0800801200")}
                    >
                        📞 Antisuicid
                    </button>
                </div>

                <button 
                    className="emergency-close-btn"
                    onClick={onClose}
                >
                    Închide
                </button>
            </div>
        </div>
    );
};

export default EmergencyPopup;