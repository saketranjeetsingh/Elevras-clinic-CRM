import { useEffect, useState } from "react";
import { get, post, put } from "../services/api";

function Treatments() {
    const [treatments, setTreatments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        treatment_name: "",
        cost: "",
        status: "",
        notes: "",
    });

    const fetchTreatments = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await get("/treatments");
            setTreatments(data || []);
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTreatments();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await post("/treatments", {
                patient_id: Number(form.patient_id),
                treatment_name: form.treatment_name,
                cost: Number(form.cost) || 0,
                status: form.status,
                notes: form.notes,
            });

            setForm({ patient_id: "", treatment_name: "", cost: "", status: "", notes: "" });
            fetchTreatments();
        } catch (err) {
            alert("Failed to create treatment: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    const handleUpdateStatus = async (t) => {
        const newStatus = window.prompt("New status", t.status || "");
        if (!newStatus) return;
        try {
            await put(`/treatments/${t.id}`, null, { status: newStatus });
            fetchTreatments();
        } catch (err) {
            alert("Failed to update status: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    return (
        <div className="page">
            <h1>Treatments</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <input name="patient_id" placeholder="Patient ID" value={form.patient_id} onChange={handleChange} />
                <input name="treatment_name" placeholder="Treatment" value={form.treatment_name} onChange={handleChange} />
                <input name="cost" placeholder="Cost" value={form.cost} onChange={handleChange} />
                <input name="status" placeholder="Status" value={form.status} onChange={handleChange} />
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <button className="btn" type="submit">Create</button>
            </form>

            {loading && <p>Loading treatments...</p>}
            {error && <p className="error">Error: {error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient ID</th>
                        <th>Treatment</th>
                        <th>Cost</th>
                        <th>Status</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {treatments.map((t) => (
                        <tr key={t.id}>
                            <td>{t.id}</td>
                            <td>{t.patient_id}</td>
                            <td>{t.treatment_name}</td>
                            <td>{t.cost}</td>
                            <td>
                                {t.status}
                                <button className="btn" onClick={() => handleUpdateStatus(t)} style={{ marginLeft: 6 }}>Update</button>
                            </td>
                            <td>{t.notes}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Treatments;

