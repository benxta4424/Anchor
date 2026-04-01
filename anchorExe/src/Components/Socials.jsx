export default function Socials() {
    return (
        <div className="socialsWrapper">
            <div className="socialsContent">
                <header className="socialsHeader">
                    <h1 className="socialsTitle">Our <span>Socials</span></h1>
                    <p className="socialsSubtitle">
                        Pentru update-uri, tweaks la motoarele noastre AI sau dacă vrei să ne contactezi într-un mod diferit... Feel free to follow us.
                    </p>
                </header>

                <div className="socialsGrid">
                    <a href="https://linkedin.com" target="_blank" rel="noreferrer" className="socialCard linkedin">
                        <div className="socialIcon">in</div>
                        <div className="socialInfo">
                            <h3>LinkedIn</h3>
                            <p>Update-uri profesionale și cercetare AI.</p>
                        </div>
                    </a>

                    <a href="https://github.com" target="_blank" rel="noreferrer" className="socialCard github">
                        <div className="socialIcon">git</div>
                        <div className="socialInfo">
                            <h3>GitHub</h3>
                            <p>Vezi codul sursă și documentația.</p>
                        </div>
                    </a>

                    <a href="https://instagram.com" target="_blank" rel="noreferrer" className="socialCard instagram">
                        <div className="socialIcon">ig</div>
                        <div className="socialInfo">
                            <h3>Instagram</h3>
                            <p>Povestea din spatele AnchorExe.</p>
                        </div>
                    </a>

                    <a href="https://twitter.com" target="_blank" rel="noreferrer" className="socialCard twitter">
                        <div className="socialIcon">X</div>
                        <div className="socialInfo">
                            <h3>Twitter / X</h3>
                            <p>Quick updates & AI news.</p>
                        </div>
                    </a>
                </div>
            </div>
        </div>
    );
}