export default function Socials() {
    return (
        <section className="socialsWrapper anim-fade-up">
            <div className="socialsContent">
                <header className="socialsHeader">
                    <h1 className="socialsTitle">Our <span className="socialsTitleAccent">Socials</span></h1>
                    <p className="socialsSubtitle">
                        Pentru update-uri, tweaks la motoarele noastre AI sau dacă dorești să ne contactezi în mod diferit... Feel free to follow us.
                    </p>
                </header>

                <div className="socialsGrid">
                    <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="socialCard linkedin" aria-label="Follow us on LinkedIn">
                        <div className="socialIcon" aria-hidden="true">in</div>
                        <div className="socialInfo">
                            <h2 className="socialCardTitle">LinkedIn</h2>
                            <p className="socialCardText">Update-uri profesionale și cercetări în domeniul inteligenței artificiale.</p>
                        </div>
                    </a>

                    <a href="https://github.com" target="_blank" rel="noreferrer" className="socialCard github" aria-label="Visit our GitHub code repository">
                        <div className="socialIcon" aria-hidden="true">git</div>
                        <div className="socialInfo">
                            <h2 className="socialCardTitle">GitHub</h2>
                            <p className="socialCardText">Vezi codul sursă, documentația completă și contribuie.</p>
                        </div>
                    </a>

                    <a href="https://instagram.com" target="_blank" rel="noreferrer" className="socialCard instagram" aria-label="Follow us on Instagram">
                        <div className="socialIcon" aria-hidden="true">ig</div>
                        <div className="socialInfo">
                            <h2 className="socialCardTitle">Instagram</h2>
                            <p className="socialCardText">Povestea din culisele dezvoltării aplicației AnchorExe.</p>
                        </div>
                    </a>

                    <a href="https://twitter.com" target="_blank" rel="noreferrer" className="socialCard twitter" aria-label="Follow us on Twitter or X">
                        <div className="socialIcon" aria-hidden="true">X</div>
                        <div className="socialInfo">
                            <h2 className="socialCardTitle">Twitter / X</h2>
                            <p className="socialCardText">Noutăți rapide și știri despre tehnologiile noastre AI.</p>
                        </div>
                    </a>
                </div>
            </div>
        </section>
    );
}