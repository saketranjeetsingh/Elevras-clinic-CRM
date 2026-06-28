import { useEffect, useState } from "react";
import { get, post, put } from "../services/api";

function Appointments() {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        doctor_name: "",
        appointment_date: "",
        status: "",
        notes: "",
    });

    const fetchAppointments = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await get("/appointments");
            setAppointments(data || []);
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
        try {
            await post("/appointments", {
                patient_id: Number(form.patient_id),
                doctor_name: form.doctor_name,
                appointment_date: form.appointment_date,
                status: form.status,
                notes: form.notes,
            });

            setForm({ patient_id: "", doctor_name: "", appointment_date: "", status: "", notes: "" });
            fetchAppointments();
        } catch (err) {
            alert("Failed to create appointment: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    const handleUpdateStatus = async (a) => {
        const newStatus = window.prompt("New status", a.status || "");
        if (!newStatus) return;
        try {
            await put(`/appointments/${a.id}`, null, { status: newStatus });
            fetchAppointments();
        } catch (err) {
            alert("Failed to update status: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    return (
        <div className="page">
            <h1>Appointments</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <input name="patient_id" placeholder="Patient ID" value={form.patient_id} onChange={handleChange} />
                <input name="doctor_name" placeholder="Doctor Name" value={form.doctor_name} onChange={handleChange} />
                <input name="appointment_date" placeholder="Date (YYYY-MM-DD)" value={form.appointment_date} onChange={handleChange} />
                <input name="status" placeholder="Status" value={form.status} onChange={handleChange} />
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <button className="btn" type="submit">Create</button>
            </form>

            {loading && <p>Loading appointments...</p>}
            {error && <p className="error">Error: {error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient ID</th>
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
                                {a.status}
                                <button className="btn" onClick={() => handleUpdateStatus(a)} style={{ marginLeft: 6 }}>Update</button>
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

