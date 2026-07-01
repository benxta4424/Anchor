import React, { useEffect, useCallback } from "react";
import { createPortal } from "react-dom";

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

    return createPortal(
        <div 
            className="emergency-popup-overlay" 
            onClick={handleOverlayClick}
            role="dialog"
            aria-modal="true"
            aria-labelledby="emergency-title"
        >
            <div className="emergency-popup">
                <div className="emergency-icon" style={{ display: 'flex', justifyContent: 'center', gap: '8px', fontSize: '32px' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#f7768e" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon siren-svg pulsing">
                        <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                        <line x1="12" x2="12" y1="9" y2="13" />
                        <line x1="12" x2="12.01" y1="17" y2="17" />
                    </svg>
                </div>
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
                        style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                            <rect x="1" y="3" width="22" height="13" rx="2" ry="2" />
                            <polyline points="17 8 17 12" />
                            <polyline points="15 10 19 10" />
                            <circle cx="6" cy="18" r="3" />
                            <circle cx="18" cy="18" r="3" />
                        </svg>
                        <span>Sună 112</span>
                    </a>
                    <button 
                        className="emergency-call-btn secondary"
                        onClick={() => handleCall("0800801200")}
                        style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
                        </svg>
                        <span>Antisuicid</span>
                    </button>
                </div>

                <button 
                    className="emergency-close-btn"
                    onClick={onClose}
                >
                    Închide
                </button>
            </div>
        </div>,
        document.body
    );
};

export default EmergencyPopup;