import { useContext } from "react";
import { Navigate } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import Sidebar from "./Sidebar";

export default function ProtectedRoute({ children }) {
    const { user, loading } = useContext(AuthContext);

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
        return <Navigate to="/" replace />;
    }

    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">{children}</main>
        </div>
    );
}
