import { Link } from "react-router-dom";

export default function InterfaceBox({ title, description, icon, boxID }) {
    return (
        <Link to={boxID} className="fpBoxOptionLink">
            <article className="fpBoxOptionContainer">
                <div className="fpBoxOptionImageWrapper">
                    <img 
                        src={icon} 
                        alt={`Icon for ${title}`} 
                        className="fpBoxOptionImage" 
                        loading="eager"
                        decoding="sync"
                    />
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