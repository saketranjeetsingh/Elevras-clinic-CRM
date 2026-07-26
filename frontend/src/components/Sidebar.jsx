import { useContext } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import Icon from "./Icon";

export default function Sidebar() {
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const doctorName = user?.doctor_name || user?.name || "Doctor";
    const clinicName = user?.clinic_name || "Your Clinic";
    const displayName = doctorName.startsWith("Dr.") ? doctorName : `Dr. ${doctorName}`;

    const handleLogout = () => {
        if (!window.confirm("Are you sure you want to logout?")) {
            return;
        }

        logout();
        navigate("/");
    };

    const navItems = [
        { to: "/dashboard", label: "Dashboard", icon: "dashboard" },
        { to: "/patients", label: "Patients", icon: "patients" },
        { to: "/appointments", label: "Appointments", icon: "appointments" },
        { to: "/treatments", label: "Treatments", icon: "treatments" },
        { to: "/bills", label: "Bills", icon: "bills" },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h2>Elevras CRM</h2>
                {user && (
                    <div className="sidebar-profile">
                        <div className="sidebar-clinic">{clinicName}</div>
                        <div className="sidebar-doctor">{displayName}</div>
                    </div>
                )}
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? "sidebar-link active" : "sidebar-link")}>
                        <Icon name={item.icon} size={16} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="sidebar-divider" />
                <button className="btn-logout" onClick={handleLogout}>
                    Logout
                </button>
            </div>
        </aside>
    );
}
