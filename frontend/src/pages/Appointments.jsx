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
        fetchAppointments();
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
            <h1>Appointments</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <div style={{ width: "100%" }}>
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
                <button className="btn" type="submit" disabled={!selectedPatient}>Create</button>
            </form>

            <PatientSummaryCard patient={selectedPatient} />

            {success && <p className="status-message success">{success}</p>}
            {loading && <p className="status-message">Loading appointments...</p>}
            {error && <p className="status-message error">{error}</p>}

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
    );
}

export default Appointments;

