import { useContext } from "react";
import { Navigate, useLocation } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import Sidebar from "./Sidebar";

const routePermissions = {
    "/dashboard": ["dashboard:view"],
    "/patients": ["patient:view"],
    "/patients/import": ["patient:create"],
    "/appointments": ["appointment:view"],
    "/treatments": ["treatment:view"],
    "/bills": ["bill:view"],
    "/settings": ["user:manage"],
};

function getRequiredPermissions(pathname) {
    for (const [route, perms] of Object.entries(routePermissions)) {
        if (pathname.startsWith(route)) {
            return perms;
        }
    }
    return [];
}

export default function ProtectedRoute({ children }) {
    const { user, loading, canAccess } = useContext(AuthContext);
    const location = useLocation();

    if (loading) {
        return (
            <div className="app-layout">
                <Sidebar />
                <main className="main-content">
                    <div className="page">
                        <div className="skeleton-card skeleton-hero" />
                        <div className="stats-grid">
                            {Array.from({ length: 4 }).map((_, index) => (
                                <div className="skeleton-card" key={index} />
                            ))}
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/" replace state={{ from: location }} />;
    }

    const requiredPermissions = getRequiredPermissions(location.pathname);
    if (requiredPermissions.length > 0 && !canAccess(requiredPermissions)) {
        return (
            <div className="app-layout">
                <Sidebar />
                <main className="main-content">
                    <div className="page">
                        <div className="card">
                            <h2>Access Denied</h2>
                            <p>You don't have permission to access this page.</p>
                            <p className="muted">Required: {requiredPermissions.join(", ")}</p>
                        </div>
                    </div>
                </main>
            </div>
        );
    }

    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">{children}</main>
        </div>
    );
}