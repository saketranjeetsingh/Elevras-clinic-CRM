import { useEffect, useMemo, useState } from "react";
import PatientSelector from "../components/PatientSelector";
import PatientSummaryCard from "../components/PatientSummaryCard";
import { get, post, put } from "../services/api";
import { createPatientLookup } from "../utils/patientHelpers";

function Treatments() {
    const [treatments, setTreatments] = useState([]);
    const [patients, setPatients] = useState([]);
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
            const [treatmentsData, patientsData] = await Promise.all([
                get("/treatments"),
                get("/patients"),
            ]);
            setTreatments(treatmentsData || []);
            setPatients(patientsData || []);
        } catch (err) {
            setError(err?.detail || err?.message || "We could not load treatments right now.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchTreatments();
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
            setError(err?.detail || err?.message || "We could not save the treatment.");
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
            setError(err?.detail || err?.message || "We could not update the treatment.");
        }
    };

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow"><span className="eyebrow-icon"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 2.8 1.7 5.2 4.2 6.3V20h5.6v-4.7A7 7 0 0 0 19 9a7 7 0 0 0-7-7Zm0 4.6a2.4 2.4 0 1 1-2.4 2.4A2.4 2.4 0 0 1 12 6.6Z" /></svg></span> Treatments</p>
                    <h1>Track care plans with confidence</h1>
                    <p className="page-subtitle">Record treatments and keep each patient’s progress visible from one view.</p>
                </div>
            </div>

            <section className="section-card form-card">
                <div className="section-heading-row">
                    <h2>Create treatment</h2>
                    <span className="muted-chip">Care tracking</span>
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
                    <input name="treatment_name" placeholder="Treatment" value={form.treatment_name} onChange={handleChange} />
                    <input name="cost" placeholder="Cost" value={form.cost} onChange={handleChange} />
                    <select name="status" value={form.status} onChange={handleChange}>
                        <option value="Planned">Planned</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                    </select>
                    <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                    <button className="btn" type="submit" disabled={!selectedPatient}>Create treatment</button>
                </form>
            </section>

            <PatientSummaryCard patient={selectedPatient} />

            {success && <div className="status-card status-card-success"><span>{success}</span></div>}
            {error && <div className="status-card status-card-error"><span>{error}</span></div>}

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Treatment list</h2>
                    <span className="muted-chip">{treatments.length} entries</span>
                </div>
                {loading ? (
                    <div className="table-skeleton">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <div className="skeleton-row" key={index} />
                        ))}
                    </div>
                ) : treatments.length > 0 ? (
                    <div className="table-wrap">
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
                                        <td>
                                            <div className="patient-cell">
                                                <span>{patientLookup.get(t.patient_id)?.name || "Unknown patient"}</span>
                                                {patientLookup.get(t.patient_id)?.phone ? (
                                                    <small>{patientLookup.get(t.patient_id).phone}</small>
                                                ) : null}
                                            </div>
                                        </td>
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
                ) : (
                    <div className="empty-state">
                        <h3>No treatments recorded.</h3>
                        <p>Create your first treatment.</p>
                    </div>
                )}
            </section>
        </div>
    );
}

export default Treatments;

