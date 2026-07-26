import { useEffect, useMemo, useState } from "react";
import PatientSelector from "../components/PatientSelector";
import PatientSummaryCard from "../components/PatientSummaryCard";
import { get, post, put } from "../services/api";
import { createPatientLookup } from "../utils/patientHelpers";

function Appointments() {
    const [appointments, setAppointments] = useState([]);
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        doctor_name: "",
        appointment_date: "",
        status: "Scheduled",
        notes: "",
    });
    const [selectedPatient, setSelectedPatient] = useState(null);

    const fetchAppointments = async () => {
        setLoading(true);
        setError(null);
        try {
            const [appointmentsData, patientsData] = await Promise.all([
                get("/appointments"),
                get("/patients"),
            ]);
            setAppointments(appointmentsData || []);
            setPatients(patientsData || []);
        } catch (err) {
            setError(err?.detail || err?.message || "We could not load appointments right now.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchAppointments();
        }, 0);

        return () => window.clearTimeout(timer);
    }, []);

    const patientLookup = useMemo(() => createPatientLookup(patients), [patients]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        if (!selectedPatient) {
            setError("Please select a patient before creating an appointment.");
            return;
        }

        try {
            await post("/appointments", {
                patient_id: Number(form.patient_id),
                doctor_name: form.doctor_name,
                appointment_date: form.appointment_date,
                status: form.status,
                notes: form.notes,
            });

            setForm({ patient_id: "", doctor_name: "", appointment_date: "", status: "Scheduled", notes: "" });
            setSelectedPatient(null);
            await fetchAppointments();
            setSuccess("Appointment created successfully");
        } catch (err) {
            setError(err?.detail || err?.message || "We could not save the appointment.");
        }
    };

    const handleUpdateStatus = async (appointment, nextStatus) => {
        setError(null);
        setSuccess(null);
        try {
            await put(`/appointments/${appointment.id}`, null, { status: nextStatus });
            await fetchAppointments();
            setSuccess("Appointment updated successfully");
        } catch (err) {
            setError(err?.detail || err?.message || "We could not update the appointment.");
        }
    };

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow"><span className="eyebrow-icon"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M7 3v2H5a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2V3h-2v2H9V3Zm12 6H5v9h14Z" /></svg></span> Appointments</p>
                    <h1>Plan the day with clarity</h1>
                    <p className="page-subtitle">Create and manage appointments without losing sight of the patient context.</p>
                </div>
            </div>

            <section className="section-card form-card">
                <div className="section-heading-row">
                    <h2>Create appointment</h2>
                    <span className="muted-chip">Quick entry</span>
                </div>
                <form onSubmit={handleCreate} className="form-grid">
                    <div className="full-width">
                        <PatientSelector
                            selectedPatient={selectedPatient}
                            onSelect={(patient) => {
                                setSelectedPatient(patient);
                                setForm((s) => ({ ...s, patient_id: patient.id }));
                            }}
                            onClear={() => {
                                setSelectedPatient(null);
                                setForm((s) => ({ ...s, patient_id: "" }));
                            }}
                        />
                    </div>
                    <input name="doctor_name" placeholder="Doctor Name" value={form.doctor_name} onChange={handleChange} />
                    <input name="appointment_date" type="date" value={form.appointment_date} onChange={handleChange} />
                    <select name="status" value={form.status} onChange={handleChange}>
                        <option value="Scheduled">Scheduled</option>
                        <option value="Completed">Completed</option>
                        <option value="Cancelled">Cancelled</option>
                    </select>
                    <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                    <button className="btn" type="submit" disabled={!selectedPatient}>Create appointment</button>
                </form>
            </section>

            <PatientSummaryCard patient={selectedPatient} />

            {success && <div className="status-card status-card-success"><span>{success}</span></div>}
            {error && <div className="status-card status-card-error"><span>{error}</span></div>}

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Appointment schedule</h2>
                    <span className="muted-chip">{appointments.length} total</span>
                </div>

                {loading ? (
                    <div className="table-skeleton">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <div className="skeleton-row" key={index} />
                        ))}
                    </div>
                ) : appointments.length > 0 ? (
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Patient</th>
                                    <th>Doctor</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                    <th>Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                                {appointments.map((a) => (
                                    <tr key={a.id}>
                                        <td>{a.id}</td>
                                        <td>
                                            <div className="patient-cell">
                                                <span>{patientLookup.get(a.patient_id)?.name || "Unknown patient"}</span>
                                                {patientLookup.get(a.patient_id)?.phone ? (
                                                    <small>{patientLookup.get(a.patient_id).phone}</small>
                                                ) : null}
                                            </div>
                                        </td>
                                        <td>{a.doctor_name}</td>
                                        <td>{a.appointment_date}</td>
                                        <td>
                                            <select value={a.status || "Scheduled"} onChange={(e) => handleUpdateStatus(a, e.target.value)}>
                                                <option value="Scheduled">Scheduled</option>
                                                <option value="Completed">Completed</option>
                                                <option value="Cancelled">Cancelled</option>
                                            </select>
                                        </td>
                                        <td>{a.notes}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <h3>No appointments yet.</h3>
                        <p>Create your first appointment.</p>
                        <button className="btn" type="button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Create appointment</button>
                    </div>
                )}
            </section>
        </div>
    );
}

export default Appointments;

