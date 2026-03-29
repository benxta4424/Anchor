import { Link } from "react-router-dom"
import InterfaceBox from "./ChooseInterfaceBox"
import textAnalyserIcon from "../img/iconBoxOne.jpg"
import faceAnalyserIcon from "../img/iconBoxTwo.jpg"
import faceAnalyserIcon2 from "../img/iconBoxTwo2.jpg"
import faceAnalyserIcon3 from "../img/iconBoxTwo3.jpeg"
import voiceAnalyserIcon from "../img/iconBoxThree.jpg"

export default function Home() {
    return (
        <>
            <div className="fpChooseBox">
                <InterfaceBox icon={textAnalyserIcon} title={"Analyze Messages"} description={"Analyse behaviour through text"} boxID={1}/>
                <InterfaceBox icon={faceAnalyserIcon} title={"Analyze Face"} description={"Analyse behaviour through facial features"} boxID={2}/>
                <InterfaceBox icon={voiceAnalyserIcon} title={"Analyze Voice"} description={"Analyse behaviour through vocal features"} boxID={3}/>
            </div>
        </>
    )
}