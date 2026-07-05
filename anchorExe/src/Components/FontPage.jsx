import React, { useState, useEffect } from "react"
import NavButtons from "./NavButtons"
import { Outlet, useLocation } from "react-router-dom"
import MiniDashboard from "./MiniDashboard"
import Home from "./Home"

// Sun and Moon Icons
const SunIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <circle cx="12" cy="12" r="4" />
    <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
  </svg>
);

const MoonIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
    <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z" />
  </svg>
);

export default function FrontPage() {
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'dark');
    const location = useLocation();
    const isRoot = location.pathname === "/";

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    return (
        <div className="fpRoot">
            {/* Ambient Background Decorative Orbs */}
            <div className="ambient-orb orb-1"></div>
            <div className="ambient-orb orb-2"></div>
            <div className="ambient-orb orb-3"></div>

            <header className="fpNavigation">
                <div className="navigationLeft">
                    <div className="heart-wrapper">
                        <div className="heart" aria-label="Emotion Heartbeat Indicator"></div>
                    </div>
                    <button 
                        className="theme-toggle-btn" 
                        onClick={toggleTheme} 
                        title={theme === 'dark' ? "Comută la modul luminos" : "Comută la modul întunecat"}
                        aria-label="Schimbă tema"
                    >
                        {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
                    </button>
                </div>

                <div className="fpActualNavButtons">              
                    <NavButtons />
                </div>
            </header>

            <main className="content">
                {/* 
                  Keep Home mounted in the DOM at all times to prevent 
                  the images from unmounting and reloading/flashing!
                */}
                <div style={{ display: isRoot ? "block" : "none", width: "100%" }}>
                    <Home />
                </div>
                <Outlet />
            </main>

            {/* Floating Mini Multimodal Dashboard Widget */}
            <MiniDashboard />
        </div>
    )
}