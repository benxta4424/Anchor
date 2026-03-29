export default function Details() {
    return (
        <div className="detailsWrapper">
            <div className="detailsContainer">
                <header className="detailsHeader">
                    <span className="thesis-badge">Licență 2026</span>
                    <h1>Anchor<span>Exe</span></h1>
                    <p style={{color:"white"}}>Sistem Inteligent de Monitorizare Multimodală</p>
                </header>

                <div className="bentoGrid">
                    <section className="detailCard missionCard">
                        <div className="cardHeader">
                            <span className="icon">⚓</span>
                            <h2>Viziune</h2>
                        </div>
                        <p>Identificăm amprenta digitală a depresiei prin AI, oferind suport invizibil dar prezent în momente critice.</p>
                    </section>

                    <div className="detailCard">
                        <h3><span className="dot text"></span>Text NLP</h3>
                        <p>Analiză semantică pentru izolarea socială și indicii lingvistice de risc.</p>
                    </div>

                    <div className="detailCard">
                        <h3><span className="dot audio"></span>Audio DSP</h3>
                        <p>Detectarea tonului monoton și a fragmentării discursului vocal.</p>
                    </div>

                    <div className="detailCard">
                        <h3><span className="dot security"></span>Security</h3>
                        <p>Procesare Edge: datele tale nu părăsesc niciodată dispozitivul.</p>
                    </div>

                    <div className="detailCard">
                        <h3><span className="dot vision"></span>Vision AI</h3>
                        <p>Clasificarea micro-expresiilor faciale prin rețele CNN avansate.</p>
                    </div>

                     <section className="emergencyBar">
                        <div className="sos-glow"></div>
                        <p style={{color:"white"}}>Ai nevoie de ajutor? Telverde Antisuicid:</p>
                        <a href="tel:0800801200" className="sosBtn">0800 801 200</a>
                    </section>
                </div>
            </div>
        </div>
    );
}