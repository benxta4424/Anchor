export default function Contact() {
    return (
        <div className="contactWrapper">
            <div className="contactHeader">
                <h2>Contactează <span>Echipa</span></h2>
                <p>Ai întrebări despre proiectul AnchorExe sau vrei să contribui?</p>
            </div>

            <form action="" className="contactForm">
                <div className="inputGroup">
                    <label htmlFor="name">Nume Complet</label>
                    <input type="text" id="name" placeholder="ex: Johnson Edward" />
                </div>

                <div className="inputGroup">
                    <label htmlFor="email">Adresa Email</label>
                    <input type="email" id="email" placeholder="ex: name@gmail.com" />
                </div>

                <div className="inputGroup">
                    <label htmlFor="message">Mesajul Tău</label>
                    <textarea id="message" name="message" placeholder="Scrie aici..."></textarea>
                </div>

                <button type="submit" className="submitBtn">
                    Trimite Mesajul <span>⚡</span>
                </button>
            </form>
        </div>
    )
}