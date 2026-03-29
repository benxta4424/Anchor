import { Link } from "react-router-dom"

// deci aici vreau sa fac fiecare buton separat si sa l generez separat in NAV
// pun link pe fiecare butonn
export default function NavButtons(props) {
    return (
        <>
            <div className="navContainer">
                <Link to="/" className="navButton"> Home </Link>
                <Link to="/details" className="navButton"> Details </Link>
                <Link to="/contact" className="navButton"> Contact </Link>
                <Link to="/socials" className="navButton"> Socials </Link>
            </div>
        </>
    )
}