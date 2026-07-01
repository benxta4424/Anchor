import { useRef, useState } from "react"
import emailjs from '@emailjs/browser';

export default function Contact() {
    const [isSending, setSending] = useState(false);
    const [toast, setToast] = useState({ show: false, type: 'success', message: '' });
    const form = useRef();

    const triggerToast = (type, message) => {
        setToast({ show: true, type, message });
        setTimeout(() => {
            setToast({ show: false, type: 'success', message: '' });
        }, 4000);
    };

    const sendEmail = (e) => {
        e.preventDefault();
        setSending(true);

        emailjs.sendForm(
            'service_1uj8g1p', 
            'template_ai35ivu', 
            form.current, 
            'kYnLJq5tgUinudjEQ'
        )
        .then((result) => {
            triggerToast("success", "Mesaj trimis cu succes! ⚡ Echipa te va contacta în cel mai scurt timp.");
            e.target.reset();
        }, (error) => {
            triggerToast("error", "Eroare la trimitere: " + error.text);
        })
        .finally(() => {
            setSending(false); // Fixed logic bug (was setSending(true))
        });
    };

    return (
        <section className="contactWrapper anim-fade-up">
            <header className="contactHeader">
                <h1 className="contactTitle">Contactează <span className="contactTitleAccent">Echipa</span></h1>
                <p className="contactSubtitle">Ai întrebări despre proiectul AnchorExe sau dorești să contribui?</p>
            </header>

            <form ref={form} onSubmit={sendEmail} className="contactForm">
                <div className="inputGroup">
                    <label htmlFor="name" className="inputLabel">Nume Complet</label>
                    <input 
                        type="text" 
                        id="name" 
                        name="name" 
                        placeholder="ex: Podean Beniamin" 
                        className="formInput"
                        required 
                    />
                </div>

                <div className="inputGroup">
                    <label htmlFor="email" className="inputLabel">Adresă Email</label>
                    <input 
                        type="email" 
                        id="email" 
                        name="user_email" 
                        placeholder="ex: name@domain.com" 
                        className="formInput"
                        required 
                    />
                </div>

                <div className="inputGroup">
                    <label htmlFor="message" className="inputLabel">Mesajul Tău</label>
                    <textarea 
                        id="message" 
                        name="message" 
                        placeholder="Cum te putem ajuta? Scrie aici..." 
                        className="formTextarea"
                        required 
                    ></textarea>
                </div>

                <button type="submit" className="submitBtn" disabled={isSending}>
                    <span>{ isSending ? "Se trimite... " : "Trimite Mesajul" }</span>
                    <span className="btnIcon" style={{ marginLeft: '6px', display: 'inline-flex', alignItems: 'center' }}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="svg-icon inline-icon">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                        </svg>
                    </span>
                </button>
            </form>

            {/* Custom Toast Alert Overlay */}
            {toast.show && (
                <div className={`toast-alert ${toast.type}`}>
                    <div className="toast-icon">
                        {toast.type === 'success' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                                <polyline points="20 6 9 17 4 12"/>
                            </svg>
                        ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" className="svg-icon">
                                <line x1="18" x2="6" y1="6" y2="18"/>
                                <line x1="6" x2="18" y1="6" y2="18"/>
                            </svg>
                        )}
                    </div>
                    <div className="toast-message">{toast.message}</div>
                </div>
            )}
        </section>
    )
}