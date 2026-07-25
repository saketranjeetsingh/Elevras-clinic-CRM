function ProfileStats({ stats, formatCurrency }) {
    return (
        <div className="stats-grid">
            <div className="card stats-card">
                <h3>Total Appointments</h3>
                <p>{stats.appointments ?? 0}</p>
            </div>
            <div className="card stats-card">
                <h3>Total Treatments</h3>
                <p>{stats.treatments ?? 0}</p>
            </div>
            <div className="card stats-card">
                <h3>Total Bills</h3>
                <p>{stats.bills ?? 0}</p>
            </div>
            <div className="card stats-card">
                <h3>Pending Amount</h3>
                <p>{formatCurrency(stats.pending_amount)}</p>
            </div>
        </div>
    );
}

export default ProfileStats;
