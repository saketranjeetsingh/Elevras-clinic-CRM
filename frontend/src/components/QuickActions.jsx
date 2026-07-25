function QuickActions({ activeAction, onSelectAction, onCancel, onSubmit, onFieldChange, quickForm }) {
    return (
        <section className="section-card">
            <div className="section-heading-row">
                <h2>Quick Actions</h2>
            </div>
            <div className="quick-actions">
                <button className="btn" type="button" onClick={() => onSelectAction("appointment")}>+ New Appointment</button>
                <button className="btn" type="button" onClick={() => onSelectAction("treatment")}>+ New Treatment</button>
                <button className="btn" type="button" onClick={() => onSelectAction("bill")}>+ Generate Bill</button>
            </div>

            {activeAction === "appointment" && (
                <form className="inline-form-card" onSubmit={onSubmit}>
                    <div className="field-label">New appointment</div>
                    <div className="form-row">
                        <input name="doctor_name" placeholder="Doctor Name" value={quickForm.appointment.doctor_name} onChange={(event) => onFieldChange("appointment", event)} />
                        <input name="appointment_date" type="date" value={quickForm.appointment.appointment_date} onChange={(event) => onFieldChange("appointment", event)} />
                        <select name="status" value={quickForm.appointment.status} onChange={(event) => onFieldChange("appointment", event)}>
                            <option value="Scheduled">Scheduled</option>
                            <option value="Completed">Completed</option>
                            <option value="Cancelled">Cancelled</option>
                        </select>
                    </div>
                    <input name="notes" placeholder="Notes" value={quickForm.appointment.notes} onChange={(event) => onFieldChange("appointment", event)} />
                    <div className="quick-form-actions">
                        <button className="btn" type="submit">Save Appointment</button>
                        <button className="btn secondary" type="button" onClick={onCancel}>Cancel</button>
                    </div>
                </form>
            )}

            {activeAction === "treatment" && (
                <form className="inline-form-card" onSubmit={onSubmit}>
                    <div className="field-label">New treatment</div>
                    <div className="form-row">
                        <input name="treatment_name" placeholder="Treatment" value={quickForm.treatment.treatment_name} onChange={(event) => onFieldChange("treatment", event)} />
                        <input name="cost" placeholder="Cost" value={quickForm.treatment.cost} onChange={(event) => onFieldChange("treatment", event)} />
                        <select name="status" value={quickForm.treatment.status} onChange={(event) => onFieldChange("treatment", event)}>
                            <option value="Planned">Planned</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Completed">Completed</option>
                        </select>
                    </div>
                    <input name="notes" placeholder="Notes" value={quickForm.treatment.notes} onChange={(event) => onFieldChange("treatment", event)} />
                    <div className="quick-form-actions">
                        <button className="btn" type="submit">Save Treatment</button>
                        <button className="btn secondary" type="button" onClick={onCancel}>Cancel</button>
                    </div>
                </form>
            )}

            {activeAction === "bill" && (
                <form className="inline-form-card" onSubmit={onSubmit}>
                    <div className="field-label">New bill</div>
                    <div className="form-row">
                        <input name="amount" placeholder="Amount" value={quickForm.bill.amount} onChange={(event) => onFieldChange("bill", event)} />
                        <select name="payment_status" value={quickForm.bill.payment_status} onChange={(event) => onFieldChange("bill", event)}>
                            <option value="Pending">Pending</option>
                            <option value="Paid">Paid</option>
                            <option value="Overdue">Overdue</option>
                        </select>
                        <select name="payment_method" value={quickForm.bill.payment_method} onChange={(event) => onFieldChange("bill", event)}>
                            <option value="Cash">Cash</option>
                            <option value="Card">Card</option>
                            <option value="Insurance">Insurance</option>
                        </select>
                    </div>
                    <div className="quick-form-actions">
                        <button className="btn" type="submit">Generate Bill</button>
                        <button className="btn secondary" type="button" onClick={onCancel}>Cancel</button>
                    </div>
                </form>
            )}
        </section>
    );
}

export default QuickActions;
