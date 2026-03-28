import NavButtons from "./NavButtons"
import InterfaceBox from "./ChooseInterfaceBox"
import { Outlet } from "react-router-dom"


export default function FrontPage() {
    return (
        <>
            <div className="fpRoot">
                <div className="fpNavigation">
                    <NavButtons  />
                </div>

                <div className="fpChooseBox">
                    
                </div>
            </div>

            <main className="content">
                <Outlet />
            </main>
        </>
    )
}