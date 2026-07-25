function RecentActivity({ lastAppointment, lastTreatment, lastBill, formatDateLabel, statusBadgeClass, formatCurrency }) {
    return (
        <section className="section-card">
            <div className="section-heading-row">
                <h2>Recent Activity</h2>
            </div>
            <div className="activity-grid">
                <div className="activity-card">
                    <div className="field-label">Last Appointment</div>
                    {lastAppointment ? (
                        <>
                            <p className="activity-date">{formatDateLabel(lastAppointment.appointment_date)}</p>
                            <span className={statusBadgeClass(lastAppointment.status)}>{lastAppointment.status || "Scheduled"}</span>
                            <p className="activity-description">{lastAppointment.notes || "Appointment recorded"}</p>
                        </>
                    ) : (
                        <p className="empty-state">No activity yet.</p>
                    )}
                </div>
                <div className="activity-card">
                    <div className="field-label">Last Treatment</div>
                    {lastTreatment ? (
                        <>
                            <p className="activity-date">{formatDateLabel(lastTreatment.appointment_date || "")}</p>
                            <span className={statusBadgeClass(lastTreatment.status)}>{lastTreatment.status || "Planned"}</span>
                            <p className="activity-description">{lastTreatment.treatment_name || "Treatment recorded"}</p>
                        </>
                    ) : (
                        <p className="empty-state">No activity yet.</p>
                    )}
                </div>
                <div className="activity-card">
                    <div className="field-label">Last Bill</div>
                    {lastBill ? (
                        <>
                            <p className="activity-date">{formatDateLabel(lastBill.payment_status || "")}</p>
                            <span className={statusBadgeClass(lastBill.payment_status)}>{lastBill.payment_status || "Pending"}</span>
                            <p className="activity-description">{formatCurrency(lastBill.amount)}</p>
                        </>
                    ) : (
                        <p className="empty-state">No activity yet.</p>
                    )}
                </div>
            </div>
        </section>
    );
}

export default RecentActivity;
