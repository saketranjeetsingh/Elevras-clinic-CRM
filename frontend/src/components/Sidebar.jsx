import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";

export default function Sidebar() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate("/");
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h2>Elevras CRM</h2>
                {user && (
                    <div className="sidebar-user">
                        {user.email || user.name}
                    </div>
                )}
            </div>

            <nav className="sidebar-nav">
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/patients">Patients</Link>
                <Link to="/appointments">Appointments</Link>
                <Link to="/treatments">Treatments</Link>
                <Link to="/bills">Bills</Link>
            </nav>

            <div className="sidebar-footer">
                <button className="btn-logout" onClick={handleLogout}>
                    Logout
                </button>
            </div>
        </aside>
    );
}
