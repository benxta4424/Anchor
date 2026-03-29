import NavButtons from "./NavButtons"
import InterfaceBox from "./ChooseInterfaceBox"
import { Outlet } from "react-router-dom"

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

                <main className="content">
                    <Outlet />
                </main>

            </div>

        </>
    )
}