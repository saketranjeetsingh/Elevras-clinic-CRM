import { useContext, useEffect, useState } from "react";
import AuthContext from "../contexts/AuthContext";
import { get } from "../services/api";

const emptyStats = {
    total_patients: 0,
    total_appointments: 0,
    total_treatments: 0,
    total_bills: 0,
    total_revenue: 0,
};

function Dashboard() {
    const { user } = useContext(AuthContext);
    const [stats, setStats] = useState(emptyStats);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await get("/dashboard/stats");
                setStats({
                    ...emptyStats,
                    ...(data || {}),
                });
            } catch (err) {
                setStats(emptyStats);
                setError(err?.detail || err?.message || "We could not load your dashboard right now.");
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    const greetingName = user?.doctor_name || user?.name || "Doctor";
    const displayName = greetingName.startsWith("Dr.") ? greetingName : `Dr. ${greetingName}`;
    const hour = new Date().getHours();
    const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

    return (
        <div className="page">
            <div className="page-header">
                <div>
                    <p className="eyebrow">Welcome back</p>
                    <h1>{greeting}, {displayName}</h1>
                    <p className="page-subtitle">{user?.clinic_name || "Your Clinic"}</p>
                    <h2>Today's Overview</h2>
                </div>
            </div>

            {loading && <p className="status-message">Loading summary...</p>}
            {error && <p className="status-message error">{error}</p>}

            <div className="stats-grid">
                <div className="card">
                    <h3>Total Patients</h3>
                    <p>{stats.total_patients}</p>
                </div>

                <div className="card">
                    <h3>Total Appointments</h3>
                    <p>{stats.total_appointments}</p>
                </div>

                <div className="card">
                    <h3>Total Treatments</h3>
                    <p>{stats.total_treatments}</p>
                </div>

                <div className="card">
                    <h3>Total Bills</h3>
                    <p>{stats.total_bills}</p>
                </div>

                <div className="card">
                    <h3>Revenue</h3>
                    <p>₹{Number(stats.total_revenue || 0).toLocaleString("en-IN")}</p>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;