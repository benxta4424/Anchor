import { useRef } from "react"
import emailjs from '@emailjs/browser';
import { useState } from "react";

export default function Contact() {

    const [isSending, setSending] = useState(false);
    const form = useRef();
    const sendEmail = (e) => {
        e.preventDefault();
        setSending(true);

        emailjs.sendForm(
            'service_1uj8g1p', 
            'template_ai35ivu', 
            form.current, 
            'kYnLJq5tgUinudjEQ')
            
            .then((result) => {
                alert("Mesaj trimis cu succes! ⚡");
                e.target.reset();
            }
            
            , (error) => {
                alert("Eroare la trimitere: " + error.text);
            })
            
            .finally(() => {
                setSending(true);
            });
    };

    return (
        <div className="contactWrapper">
            <div className="contactHeader">
                <h2>Contactează <span>Echipa</span></h2>
                <p>Ai întrebări despre proiectul AnchorExe sau vrei să contribui?</p>
            </div>

            <form ref={form} onSubmit={sendEmail} action="" className="contactForm">
                <div className="inputGroup">
                    <label htmlFor="name">Nume Complet</label>
                    <input type="text" id="name" name="name" placeholder="ex: Johnson Edward" required />
                </div>

                <div className="inputGroup">
                    <label htmlFor="email">Adresa Email</label>
                    <input type="email" id="email" name="user_email" placeholder="ex: name@gmail.com" required />
                </div>

                <div className="inputGroup">
                    <label htmlFor="message">Mesajul Tău</label>
                    <textarea id="message" name="message" placeholder="Scrie aici..." required></textarea>
                </div>

                <button type="submit" className="submitBtn" disabled={isSending}>
                    { isSending ? "Se trimite.. " : "Trimite Mesajul" } <span>⚡</span>
                </button>
            </form>
        </div>
    )
}