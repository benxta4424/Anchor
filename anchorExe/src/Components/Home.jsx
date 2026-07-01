import { Link } from "react-router-dom"
import InterfaceBox from "./ChooseInterfaceBox"
import textAnalyserIcon from "../img/iconBoxOne.jpg"
import faceAnalyserIcon from "../img/iconBoxTwo.jpg"
import voiceAnalyserIcon from "../img/iconBoxThree.jpg"

export default function Home() {
    return (
        <section className="homeSection anim-fade-up">
            <header className="homeHeader">
                <h1 className="homeTitle">MULTIMODAL RECOGNITION</h1>
                <p className="homeSubtitle">
                    Select an analyzer interface below to decipher, track, and log emotional states in real-time.
                </p>
            </header>

            <div className="fpChooseBox">
                <InterfaceBox icon={textAnalyserIcon} title={"Analyze Messages"} description={"Extract sentiments, tone indicators, and intent from textual inputs."} boxID={"/text_analiser"}/>
                <InterfaceBox icon={faceAnalyserIcon} title={"Analyze Face"} description={"Detect facial micro-expressions and identify emotional states live."} boxID={"/face_analiser"}/>
                <InterfaceBox icon={voiceAnalyserIcon} title={"Analyze Voice"} description={"Process pitch patterns, energy thresholds, and decibel signals."} boxID={"/voice_analiser"}/>
            </div>
        </section>
    )
}