function HistoryTables({ appointments, treatments, bills, formatCurrency, statusBadgeClass }) {
    return (
        <>
            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Appointment History</h2>
                </div>
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {appointments.length === 0 ? (
                                <tr>
                                    <td colSpan="2" className="empty-state">No appointments found for this patient.</td>
                                </tr>
                            ) : (
                                appointments.map((appointment) => (
                                    <tr key={appointment.id}>
                                        <td>{appointment.appointment_date || "—"}</td>
                                        <td>
                                            <span className={statusBadgeClass(appointment.status)}>{appointment.status || "Unknown"}</span>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Treatment History</h2>
                </div>
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Treatment</th>
                                <th>Status</th>
                                <th>Doctor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {treatments.length === 0 ? (
                                <tr>
                                    <td colSpan="3" className="empty-state">No treatments found for this patient.</td>
                                </tr>
                            ) : (
                                treatments.map((treatment) => (
                                    <tr key={treatment.id}>
                                        <td>{treatment.treatment_name || "—"}</td>
                                        <td>
                                            <span className={statusBadgeClass(treatment.status)}>{treatment.status || "Unknown"}</span>
                                        </td>
                                        <td>{treatment.doctor_name || "—"}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </section>

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Billing History</h2>
                </div>
                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Amount</th>
                                <th>Paid / Pending</th>
                                <th>Payment Method</th>
                            </tr>
                        </thead>
                        <tbody>
                            {bills.length === 0 ? (
                                <tr>
                                    <td colSpan="3" className="empty-state">No billing history found for this patient.</td>
                                </tr>
                            ) : (
                                bills.map((bill) => (
                                    <tr key={bill.id}>
                                        <td>{formatCurrency(bill.amount)}</td>
                                        <td>
                                            <span className={statusBadgeClass(bill.payment_status)}>{bill.payment_status || "Pending"}</span>
                                        </td>
                                        <td>{bill.payment_method || "—"}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </section>
        </>
    );
}

export default HistoryTables;
