import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { get } from "../services/api";

function formatCurrency(value) {
    const amount = Number(value || 0);
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
    }).format(amount);
}

function statusBadgeClass(status) {
    const normalized = String(status || "").toLowerCase();

    if (normalized.includes("paid") || normalized.includes("completed") || normalized.includes("done")) {
        return "status-badge success";
    }

    if (normalized.includes("cancel") || normalized.includes("overdue")) {
        return "status-badge danger";
    }

    return "status-badge neutral";
}

function PatientProfile() {
    const { id } = useParams();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchProfile = async () => {
            setLoading(true);
            setError(null);

            try {
                const data = await get(`/patients/${id}/profile`);
                setProfile(data || null);
            } catch (err) {
                setError(err?.detail || err?.message || "We could not load the patient profile.");
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchProfile();
        }
    }, [id]);

    const patient = profile?.patient || {};
    const appointments = profile?.appointments || [];
    const treatments = profile?.treatments || [];
    const bills = profile?.bills || [];
    const stats = profile?.stats || {};

    return (
        <div className="page">
            <div className="page-header">
                <Link to="/patients" className="back-link">← Back to Patients</Link>
                <div className="eyebrow">Patient profile</div>
                <h1>{patient.name || "Patient"}</h1>
                <p className="page-subtitle">Complete medical record and visit history</p>
            </div>

            {loading && <p className="status-message">Loading patient profile...</p>}
            {error && <p className="status-message error">{error}</p>}

            {!loading && !error && profile && (
                <div className="profile-layout">
                    <section className="card profile-card">
                        <div className="section-heading-row">
                            <h2>Patient Information</h2>
                            <span className="muted-chip">ID #{patient.id}</span>
                        </div>

                        <div className="info-grid">
                            <div><span className="field-label">Name</span><p>{patient.name || "—"}</p></div>
                            <div><span className="field-label">Age</span><p>{patient.age || "—"}</p></div>
                            <div><span className="field-label">Gender</span><p>{patient.gender || "—"}</p></div>
                            <div><span className="field-label">Phone</span><p>{patient.phone || "—"}</p></div>
                            <div><span className="field-label">Email</span><p>{patient.email || "—"}</p></div>
                            <div><span className="field-label">Address</span><p>{patient.address || "—"}</p></div>
                            <div><span className="field-label">Blood Group</span><p>{patient.blood_group || "—"}</p></div>
                            <div><span className="field-label">Medical History</span><p>{patient.medical_history || "—"}</p></div>
                            <div><span className="field-label">Last Treatment Date</span><p>{patient.last_treatment || "—"}</p></div>
                        </div>
                    </section>

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
                </div>
            )}
        </div>
    );
}

export default PatientProfile;
