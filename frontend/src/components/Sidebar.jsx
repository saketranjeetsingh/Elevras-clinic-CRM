import { useContext, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import Icon from "./Icon";
import ConfirmModal from "./ConfirmModal";
import { useTheme } from "./ThemeContext";

export default function Sidebar() {
    const { user, logout } = useContext(AuthContext);
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const [logoutOpen, setLogoutOpen] = useState(false);

    const doctorName = user?.doctor_name || user?.name || "Doctor";
    const clinicName = user?.clinic_name || "Your Clinic";
    const displayName = doctorName.startsWith("Dr.") ? doctorName : `Dr. ${doctorName}`;

    const handleLogout = () => {
        setLogoutOpen(false);
        logout();
        navigate("/");
    };

    const navItems = [
        { to: "/dashboard", label: "Dashboard", icon: "dashboard" },
        { to: "/patients", label: "Patients", icon: "patients" },
        { to: "/patients/import", label: "Import Patients", icon: "import" },
        { to: "/appointments", label: "Appointments", icon: "appointments" },
        { to: "/treatments", label: "Treatments", icon: "treatments" },
        { to: "/bills", label: "Bills", icon: "bills" },
    ];

    const isDark = theme === "dark";

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="brand-block">
                    <div className="brand-mark">
                        <Icon name="medical" size={20} />
                    </div>
                    <div className="brand-text">
                        <span className="brand-title">Elevras</span>
                        <span className="brand-subtitle">ClinicOS</span>
                    </div>
                </div>
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
                        <Icon name={item.icon} size={18} />
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <button className="theme-toggle" type="button" onClick={toggleTheme} aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}>
                    <Icon name={isDark ? "sun" : "moon"} size={16} />
                    <span>{isDark ? "Light mode" : "Dark mode"}</span>
                </button>
                <div className="sidebar-divider" />
                <button className="btn-logout" type="button" onClick={() => setLogoutOpen(true)}>
                    <Icon name="logout" size={16} />
                    Logout
                </button>
            </div>

            <ConfirmModal
                open={logoutOpen}
                title="Log out?"
                message="Are you sure you want to log out?"
                confirmLabel="Log out"
                onConfirm={handleLogout}
                onCancel={() => setLogoutOpen(false)}
            />
        </aside>
    );
}