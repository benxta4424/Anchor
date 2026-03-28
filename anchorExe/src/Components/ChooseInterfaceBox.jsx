import { Link } from "react-router-dom";

export default function InterfaceBox({ title, description, icon, boxID }) {
    return (
        <>
            <Link to={boxID} className="fpBoxOptionLink">
                <div className="fpBoxOptionContainer">
                    <div className="fpBoxOptionIcon">
                        <img src={icon} alt="" style={{width: '100px', height:'200x', borderRadius:"20px"}} />
                    </div>

                    <div className="fpBoxOptionTitle">{title}</div>
                    <div className="fpBoxOptionDescription">{description}</div>
                </div>
            </Link>
        </>    
    );
}