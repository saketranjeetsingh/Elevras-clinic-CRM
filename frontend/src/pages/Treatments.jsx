import { useEffect, useState } from "react";
import PatientSelector from "../components/PatientSelector";
import { get, post, put } from "../services/api";

function Treatments() {
    const [treatments, setTreatments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        treatment_name: "",
        cost: "",
        status: "Planned",
        notes: "",
    });
    const [selectedPatient, setSelectedPatient] = useState(null);

    const fetchTreatments = async () => {
        setLoading(true);
        setError(null);
        try {
            const [treatmentsData] = await Promise.all([
                get("/treatments"),
            ]);
            setTreatments(treatmentsData || []);
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
        setError(null);
        setSuccess(null);

        if (!selectedPatient) {
            setError("Please select a patient before creating a treatment.");
            return;
        }

        try {
            await post("/treatments", {
                patient_id: Number(form.patient_id),
                treatment_name: form.treatment_name,
                cost: Number(form.cost) || 0,
                status: form.status,
                notes: form.notes,
            });

            setForm({ patient_id: "", treatment_name: "", cost: "", status: "Planned", notes: "" });
            setSelectedPatient(null);
            await fetchTreatments();
            setSuccess("Treatment created successfully");
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    const handleUpdateStatus = async (treatment, nextStatus) => {
        setError(null);
        setSuccess(null);
        try {
            await put(`/treatments/${treatment.id}`, null, { status: nextStatus });
            await fetchTreatments();
            setSuccess("Treatment updated successfully");
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    return (
        <div className="page">
            <h1>Treatments</h1>

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
                <input name="treatment_name" placeholder="Treatment" value={form.treatment_name} onChange={handleChange} />
                <input name="cost" placeholder="Cost" value={form.cost} onChange={handleChange} />
                <select name="status" value={form.status} onChange={handleChange}>
                    <option value="Planned">Planned</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                </select>
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <button className="btn" type="submit" disabled={!selectedPatient}>Create</button>
            </form>

            {selectedPatient && (
                <div className="patient-summary-card">
                    <div className="field-label">Selected patient</div>
                    <div className="patient-summary-row">
                        <strong>{selectedPatient.name || "Patient"}</strong>
                        <span>{selectedPatient.age ? `${selectedPatient.age} yrs` : "Age not provided"}</span>
                    </div>
                    <div className="patient-summary-row">
                        <span>{selectedPatient.gender || "Gender not provided"}</span>
                        <span>{selectedPatient.phone || "No phone provided"}</span>
                    </div>
                </div>
            )}

            {success && <p className="success">{success}</p>}
            {loading && <p>Loading treatments...</p>}
            {error && <p className="error">Error: {error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient</th>
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
                                <select value={t.status || "Planned"} onChange={(e) => handleUpdateStatus(t, e.target.value)}>
                                    <option value="Planned">Planned</option>
                                    <option value="In Progress">In Progress</option>
                                    <option value="Completed">Completed</option>
                                </select>
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

