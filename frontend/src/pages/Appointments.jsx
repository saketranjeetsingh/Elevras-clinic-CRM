import { useEffect, useState } from "react";
import { get, post, put } from "../services/api";

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
            setError(err?.detail || err?.message || JSON.stringify(err));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAppointments();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);

        try {
            await post("/appointments", {
                patient_id: Number(form.patient_id),
                doctor_name: form.doctor_name,
                appointment_date: form.appointment_date,
                status: form.status,
                notes: form.notes,
            });

            setForm({ patient_id: "", doctor_name: "", appointment_date: "", status: "Scheduled", notes: "" });
            await fetchAppointments();
            setSuccess("Appointment created successfully");
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
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
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    return (
        <div className="page">
            <h1>Appointments</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <select name="patient_id" value={form.patient_id} onChange={handleChange}>
                    <option value="">Select patient</option>
                    {patients.map((patient) => (
                        <option key={patient.id} value={patient.id}>{patient.name} ({patient.phone})</option>
                    ))}
                </select>
                <input name="doctor_name" placeholder="Doctor Name" value={form.doctor_name} onChange={handleChange} />
                <input name="appointment_date" placeholder="Date (YYYY-MM-DD)" value={form.appointment_date} onChange={handleChange} />
                <select name="status" value={form.status} onChange={handleChange}>
                    <option value="Scheduled">Scheduled</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <button className="btn" type="submit">Create</button>
            </form>

            {success && <p className="success">{success}</p>}
            {loading && <p>Loading appointments...</p>}
            {error && <p className="error">Error: {error}</p>}

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
                            <td>{a.patient_id}</td>
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

