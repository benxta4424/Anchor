import { NavLink } from "react-router-dom"

export default function NavButtons() {
    return (
        <nav className="navContainer" aria-label="Main navigation">
            <NavLink to="/" end className={({ isActive }) => isActive ? "navButton active" : "navButton"}>
                Home
            </NavLink>
            <NavLink to="/details" className={({ isActive }) => isActive ? "navButton active" : "navButton"}>
                Details
            </NavLink>
            <NavLink to="/contact" className={({ isActive }) => isActive ? "navButton active" : "navButton"}>
                Contact
            </NavLink>
            <NavLink to="/socials" className={({ isActive }) => isActive ? "navButton active" : "navButton"}>
                Socials
            </NavLink>
        </nav>
    )
}