import { Link } from "react-router-dom";

export default function InterfaceBox({ title, description, boxID }) {
    const renderVisual = () => {
        if (boxID === "/text_analiser") {
            return (
                <svg className="fpBoxSvgVisual" viewBox="0 0 400 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="textGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#7aa2f7" />
                            <stop offset="100%" stopColor="#bb9af7" />
                        </linearGradient>
                        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="#0a0c16" />
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    <g transform="translate(140, 40)">
                        <circle cx="60" cy="60" r="50" stroke="url(#textGrad)" strokeWidth="1.5" strokeDasharray="5, 5" opacity="0.3" />
                        <circle cx="60" cy="60" r="40" stroke="url(#textGrad)" strokeWidth="2" opacity="0.6" />
                        <rect x="42" y="47" width="36" height="26" rx="4" fill="rgba(122, 162, 247, 0.15)" stroke="url(#textGrad)" strokeWidth="2" />
                        <line x1="48" y1="54" x2="64" y2="54" stroke="#7aa2f7" strokeWidth="2" strokeLinecap="round" />
                        <line x1="48" y1="60" x2="72" y2="60" stroke="#bb9af7" strokeWidth="2" strokeLinecap="round" />
                        <line x1="48" y1="66" x2="58" y2="66" stroke="#7aa2f7" strokeWidth="2" strokeLinecap="round" />
                        <line x1="20" y1="60" x2="100" y2="60" stroke="#7aa2f7" strokeWidth="2" opacity="0.8" />
                        <line x1="20" y1="60" x2="100" y2="60" stroke="#bb9af7" strokeWidth="4" opacity="0.3" />
                    </g>
                    <text x="50%" y="175" textAnchor="middle" fill="rgba(255, 255, 255, 0.3)" fontSize="10" fontFamily="monospace" letterSpacing="2">SEMANTIC ANALYSIS ENGINE</text>
                </svg>
            );
        } else if (boxID === "/face_analiser") {
            return (
                <svg className="fpBoxSvgVisual" viewBox="0 0 400 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="faceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#bb9af7" />
                            <stop offset="100%" stopColor="#f7768e" />
                        </linearGradient>
                        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="#0a0c16" />
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    <g transform="translate(140, 35)">
                        <circle cx="60" cy="65" r="55" stroke="url(#faceGrad)" strokeWidth="1" strokeDasharray="3, 3" opacity="0.4" />
                        <path d="M 20 65 L 100 65" stroke="url(#faceGrad)" strokeWidth="0.5" opacity="0.3" />
                        <path d="M 60 25 L 60 105" stroke="url(#faceGrad)" strokeWidth="0.5" opacity="0.3" />
                        <circle cx="60" cy="45" r="3" fill="#f7768e" />
                        <circle cx="45" cy="55" r="2.5" fill="#bb9af7" />
                        <circle cx="75" cy="55" r="2.5" fill="#bb9af7" />
                        <circle cx="50" cy="70" r="2" fill="#bb9af7" />
                        <circle cx="70" cy="70" r="2" fill="#bb9af7" />
                        <circle cx="60" cy="85" r="3" fill="#f7768e" />
                        <path d="M 60 45 L 45 55 L 50 70 L 60 85 L 70 70 L 75 55 Z" stroke="url(#faceGrad)" strokeWidth="1" strokeLinejoin="round" opacity="0.6" />
                        <path d="M 60 45 L 50 70 M 60 45 L 70 70 M 45 55 L 75 55 M 50 70 L 70 70" stroke="url(#faceGrad)" strokeWidth="0.5" opacity="0.4" />
                    </g>
                    <text x="50%" y="175" textAnchor="middle" fill="rgba(255, 255, 255, 0.3)" fontSize="10" fontFamily="monospace" letterSpacing="2">BIOMETRIC MESH SCANNER</text>
                </svg>
            );
        } else if (boxID === "/voice_analiser") {
            return (
                <svg className="fpBoxSvgVisual" viewBox="0 0 400 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="voiceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stopColor="#73daca" />
                            <stop offset="100%" stopColor="#7aa2f7" />
                        </linearGradient>
                        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(255, 255, 255, 0.03)" strokeWidth="1" />
                        </pattern>
                    </defs>
                    <rect width="100%" height="100%" fill="#0a0c16" />
                    <rect width="100%" height="100%" fill="url(#grid)" />
                    <g transform="translate(100, 50)">
                        <path d="M 10 50 Q 30 10, 50 50 T 90 50 T 130 50 T 170 50 T 200 50" stroke="url(#voiceGrad)" strokeWidth="2.5" strokeLinecap="round" opacity="0.8" />
                        <path d="M 10 50 Q 30 25, 50 50 T 90 50 T 130 50 T 170 50 T 200 50" stroke="#7aa2f7" strokeWidth="1.5" strokeLinecap="round" opacity="0.4" />
                        <rect x="35" y="15" width="4" height="25" rx="2" fill="#73daca" opacity="0.3" />
                        <rect x="75" y="5" width="4" height="45" rx="2" fill="#73daca" opacity="0.5" />
                        <rect x="115" y="20" width="4" height="20" rx="2" fill="#7aa2f7" opacity="0.5" />
                        <rect x="155" y="10" width="4" height="35" rx="2" fill="#7aa2f7" opacity="0.3" />
                    </g>
                    <text x="50%" y="175" textAnchor="middle" fill="rgba(255, 255, 255, 0.3)" fontSize="10" fontFamily="monospace" letterSpacing="2">PROSODIC SPECTRAL ANALYZER</text>
                </svg>
            );
        }
        return null;
    };

    return (
        <Link to={boxID} className="fpBoxOptionLink">
            <article className="fpBoxOptionContainer">
                <div className="fpBoxOptionImageWrapper">
                    {renderVisual()}
                    <div className="fpBoxOptionOverlay">
                        <span className="fpBoxOptionCta">Launch →</span>
                    </div>
                </div>

                <div className="fpBoxOptionText">
                    <h2 className="fpBoxOptionTitle">{title}</h2>
                    <p className="fpBoxOptionDescription">{description}</p>
                </div>
            </article>
        </Link>
    );
}