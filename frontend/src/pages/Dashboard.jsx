import { useEffect, useState } from "react";
import { get } from "../services/api";

function Dashboard() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStats = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await get("/dashboard/stats");
                setStats(data);
            } catch (err) {
                setError(err?.detail || err?.message || JSON.stringify(err));
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    return (
        <div className="page">
            <h1>Dashboard</h1>

            {loading && <p>Loading...</p>}
            {error && <p className="error">Error: {error}</p>}

            {stats && (
                <div className="stats-grid">
                    <div className="card">
                        <h3>Total Patients</h3>
                        <p>{stats.total_patients}</p>
                    </div>

                    <div className="card">
                        <h3>Appointments</h3>
                        <p>{stats.total_appointments}</p>
                    </div>

                    <div className="card">
                        <h3>Treatments</h3>
                        <p>{stats.total_treatments}</p>
                    </div>

                    <div className="card">
                        <h3>Bills</h3>
                        <p>{stats.total_bills}</p>
                    </div>

                    <div className="card">
                        <h3>Total Revenue</h3>
                        <p>${stats.total_revenue}</p>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Dashboard;