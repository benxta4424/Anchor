import NavButtons from "./NavButtons"
import InterfaceBox from "./ChooseInterfaceBox"
import { Outlet } from "react-router-dom"
import textAnalyserIcon from "../img/iconBoxOne.jpg"
import faceAnalyserIcon from "../img/iconBoxTwo.jpg"
import faceAnalyserIcon2 from "../img/iconBoxTwo2.jpg"
import faceAnalyserIcon3 from "../img/iconBoxTwo3.jpeg"
import voiceAnalyserIcon from "../img/iconBoxThree.jpg"

export default function FrontPage() {
    return (
        <>
            <div className="fpRoot">

                <div className="fpNavigation">
                    <div className="heart-wrapper">
                        <div className="heart"></div>
                    </div>

                    <div className="fpActualNavButtons">              
                        <NavButtons  />
                    </div>
                </div>

                <div className="fpChooseBox">
                    <InterfaceBox icon={textAnalyserIcon} title={"Analyze Messages"} description={"Analyse behaviour through text"} boxID={1}/>
                    <InterfaceBox icon={faceAnalyserIcon} title={"Analyze Face"} description={"Analyse behaviour through facial features"} boxID={2}/>
                    <InterfaceBox icon={voiceAnalyserIcon} title={"Analyze Voice"} description={"Analyse behaviour through vocal features"} boxID={3}/>
                </div>

            </div>

            <main className="content">
                <Outlet />
            </main>
        </>
    )
}