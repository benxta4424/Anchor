export default function Details() {
    return (
        <section className="detailsWrapper anim-fade-up">
            <div className="detailsContainer">
                <header className="detailsHeader">
                    <span className="thesis-badge">Licență 2026</span>
                    <h1 className="detailsTitle">Anchor<span className="detailsTitleAccent">Exe</span></h1>
                    <p className="detailsSubtitle">Sistem Inteligent de Monitorizare Multimodală</p>
                </header>

                <div className="bentoGrid">
                    <article className="detailCard missionCard">
                        <header className="cardHeader">
                            <span className="icon" role="img" aria-label="anchor">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                                    <circle cx="12" cy="5" r="2" />
                                    <line x1="12" x2="12" y1="7" y2="21" />
                                    <path d="M5 12H2a10 10 0 0 0 20 0h-3" />
                                    <circle cx="12" cy="12" r="1.5" />
                                </svg>
                            </span>
                            <h2 className="cardTitle">Viziune</h2>
                        </header>
                        <p className="cardText">
                            Identificăm amprenta digitală a stărilor de depresie prin inteligență artificială, oferind un suport invizibil dar mereu prezent în momentele critice.
                        </p>
                    </article>

                    <article className="detailCard">
                        <header className="cardHeader">
                            <span className="dot text"></span>
                            <h3 className="cardTitleSmall">Text NLP</h3>
                        </header>
                        <p className="cardText">
                            Analiză semantică și sintactică avansată pentru decodarea izolării sociale și determinarea indicilor lingvistice de risc.
                        </p>
                    </article>

                    <article className="detailCard">
                        <header className="cardHeader">
                            <span className="dot audio"></span>
                            <h3 className="cardTitleSmall">Audio DSP</h3>
                        </header>
                        <p className="cardText">
                            Procesare de semnal audio în timp real pentru detectarea tonului monoton, a aplatizării afective și a fragmentării discursului.
                        </p>
                    </article>

                    <article className="detailCard">
                        <header className="cardHeader">
                            <span className="dot security"></span>
                            <h3 className="cardTitleSmall">Security</h3>
                        </header>
                        <p className="cardText">
                            Confidențialitate garantată prin procesare locală tip Edge. Datele tale biometrice nu părăsesc niciodată dispozitivul.
                        </p>
                    </article>

                    <article className="detailCard">
                        <header className="cardHeader">
                            <span className="dot vision"></span>
                            <h3 className="cardTitleSmall">Vision AI</h3>
                        </header>
                        <p className="cardText">
                            Clasificare în timp real a micro-expresiilor faciale prin intermediul unei rețele neuronale convoluționale (CNN).
                        </p>
                    </article>

                    <section className="emergencyBar">
                        <div className="sos-glow"></div>
                        <p className="emergencyText">Ai nevoie de ajutor? Telverde Antisuicid (non-stop):</p>
                        <a href="tel:0800801200" className="sosBtn" aria-label="Sună la Telverde Antisuicid">0800 801 200</a>
                    </section>
                </div>
            </div>
        </section>
    );
}