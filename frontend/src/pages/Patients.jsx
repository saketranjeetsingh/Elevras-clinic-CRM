import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { get, post, put, del } from "../services/api";
import { useToast } from "../components/ToastContext";
import ConfirmModal from "../components/ConfirmModal";

function Patients() {
    const [patients, setPatients] = useState([]);
    const [allPatients, setAllPatients] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [form, setForm] = useState({
        name: "",
        phone: "",
        email: "",
        age: "",
        gender: "",
        blood_group: "",
        medical_history: "",
        notes: "",
    });
    const [editingId, setEditingId] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");
    const [pendingDeleteId, setPendingDeleteId] = useState(null);
    const toast = useToast();

    const emptyForm = {
        name: "",
        phone: "",
        email: "",
        age: "",
        gender: "",
        blood_group: "",
        medical_history: "",
        notes: "",
    };

    const fetchPatients = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await get("/patients");
            const patientList = data || [];
            setAllPatients(patientList);
            setPatients(patientList);
        } catch (err) {
            setError(err?.detail || err?.message || "We could not load patients right now.");
            toast.error(err?.detail || err?.message || "We could not load patients right now.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchPatients();
        }, 0);

        return () => window.clearTimeout(timer);
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        setError(null);

        if (!form.name.trim() || !form.phone.trim()) {
            toast.error("Please enter the patient name and phone number.");
            return;
        }

        try {
            if (editingId) {
                await put(`/patients/${editingId}`, {
                    name: form.name,
                    phone: form.phone,
                    email: form.email || null,
                    age: Number(form.age) || 0,
                    gender: form.gender,
                    blood_group: form.blood_group,
                    medical_history: form.medical_history,
                    notes: form.notes,
                });

                toast.success("Patient updated successfully");
                setEditingId(null);
            } else {
                await post("/patients", {
                    name: form.name,
                    phone: form.phone,
                    email: form.email || null,
                    age: Number(form.age) || 0,
                    gender: form.gender,
                    blood_group: form.blood_group,
                    medical_history: form.medical_history,
                    notes: form.notes,
                });

                toast.success("Patient created successfully");
            }

            setForm(emptyForm);
            await fetchPatients();
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not save the patient record.");
        }
    };

    const handleEdit = (patient) => {
        setEditingId(patient.id);
        setForm({
            name: patient.name || "",
            phone: patient.phone || "",
            email: patient.email || "",
            age: patient.age || "",
            gender: patient.gender || "",
            blood_group: patient.blood_group || "",
            medical_history: patient.medical_history || "",
            notes: patient.notes || "",
        });
        setError(null);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setForm(emptyForm);
    };

    const handleDeleteConfirm = async () => {
        if (!pendingDeleteId) {
            return;
        }

        const deleteId = pendingDeleteId;
        setPendingDeleteId(null);

        try {
            await del(`/patients/${deleteId}`);
            toast.success("Patient deleted successfully");
            await fetchPatients();
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not delete the patient record.");
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        const query = searchQuery.trim();

        if (!query) {
            setPatients(allPatients);
            return;
        }

        const normalizedQuery = query.toLowerCase();
        const emailPattern = /[^\s@]+@[^\s@]+\.[^\s@]+/;
        const phonePattern = /^\+?[\d\s()-]{4,}$/;

        const filtered = allPatients.filter((patient) => {
            const values = [
                patient.name,
                patient.phone,
                patient.email,
            ];

            if (emailPattern.test(normalizedQuery)) {
                return values.some((value) => String(value || "").toLowerCase().includes(normalizedQuery));
            }

            if (phonePattern.test(normalizedQuery)) {
                return String(patient.phone || "").toLowerCase().includes(normalizedQuery);
            }

            return values.some((value) => String(value || "").toLowerCase().includes(normalizedQuery));
        });

        setPatients(filtered);
    };

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow"><span className="eyebrow-icon"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M16 8a3 3 0 1 0-3-3 3 3 0 0 0 3 3Zm-8 0a3 3 0 1 0-3-3 3 3 0 0 0 3 3Zm0 2c-2.8 0-5 1.6-5 3.6V16h10v-2.4C13 11.6 10.8 10 8 10Zm8 0c-.7 0-1.4.1-2 .3a4.2 4.2 0 0 1 0 3.7c1.4.4 2 1 2 1.6V16h4v-2.4c0-2-2.2-3.6-4-3.6Z" /></svg></span> Patients</p>
                    <h1>Keep your patient roster organised</h1>
                    <p className="page-subtitle">Capture personal details, treatment history, and the next best follow-up in one place.</p>
                </div>
            </div>

            <section className="section-card form-card">
                <div className="section-heading-row">
                    <h2>{editingId ? "Update patient" : "Add patient"}</h2>
                    <span className="muted-chip">Patient details</span>
                </div>
                <form onSubmit={handleCreate} className="form-grid">
                    <div className="form-field">
                        <label htmlFor="patient-name">Name <span className="muted">(required)</span></label>
                        <input id="patient-name" name="name" placeholder="Full name" value={form.name} onChange={handleChange} required />
                    </div>
                    <div className="form-field">
                        <label htmlFor="patient-phone">Phone <span className="muted">(required)</span></label>
                        <input id="patient-phone" name="phone" placeholder="Phone number" value={form.phone} onChange={handleChange} required />
                    </div>
                    <div className="form-field">
                        <label htmlFor="patient-email">Email <span className="muted">(optional)</span></label>
                        <input id="patient-email" name="email" type="email" placeholder="Email (optional)" value={form.email} onChange={handleChange} />
                    </div>
                    <div className="form-field">
                        <label htmlFor="patient-age">Age</label>
                        <input id="patient-age" name="age" type="number" min="0" placeholder="Age" value={form.age} onChange={handleChange} />
                    </div>
                    <div className="form-field">
                        <label htmlFor="patient-gender">Gender</label>
                        <input id="patient-gender" name="gender" placeholder="Gender" value={form.gender} onChange={handleChange} />
                    </div>
                    <div className="form-field">
                        <label htmlFor="patient-blood-group">Blood Group</label>
                        <input id="patient-blood-group" name="blood_group" placeholder="Blood group" value={form.blood_group} onChange={handleChange} />
                    </div>
                    <div className="form-field full-width">
                        <label htmlFor="patient-medical-history">Medical History</label>
                        <textarea id="patient-medical-history" name="medical_history" rows="3" placeholder="Allergies, conditions, ongoing care…" value={form.medical_history} onChange={handleChange} />
                    </div>
                    <div className="form-field full-width">
                        <label htmlFor="patient-notes">Notes</label>
                        <textarea id="patient-notes" name="notes" rows="2" placeholder="Internal notes" value={form.notes} onChange={handleChange} />
                    </div>
                    <div className="full-width action-row">
                        <button className="btn" type="submit">{editingId ? "Save changes" : "Create patient"}</button>
                        {editingId && <button type="button" className="btn secondary" onClick={handleCancelEdit}>Cancel</button>}
                    </div>
                </form>
            </section>

            <section className="section-card">
                <form onSubmit={handleSearch} className="search-row">
                    <input placeholder="Search by name, phone, email, or treatment" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                    <button className="btn" type="submit">Search</button>
                    <button className="btn secondary" type="button" onClick={() => { setSearchQuery(""); setPatients(allPatients); }}>Clear</button>
                </form>
            </section>

            {error && <div className="status-card status-card-error"><span>{error}</span></div>}

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Patient roster</h2>
                    <span className="muted-chip">{patients.length} patients</span>
                </div>
                {loading ? (
                    <div className="table-skeleton">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <div className="skeleton-row" key={index} />
                        ))}
                    </div>
                ) : patients.length > 0 ? (
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Phone</th>
                                    <th>Email</th>
                                    <th>Age</th>
                                    <th>Gender</th>
                                    <th>Last Treatment</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {patients.map((p) => (
                                    <tr key={p.id}>
                                        <td>
                                            <Link to={`/patients/${p.id}`} className="patient-link">{p.id}</Link>
                                        </td>
                                        <td>
                                            <Link to={`/patients/${p.id}`} className="patient-link">{p.name}</Link>
                                            {!p.age && !p.gender && !p.email && !p.medical_history && (
                                                <span className="badge badge-warning">Needs details</span>
                                            )}
                                        </td>
                                        <td>{p.phone}</td>
                                        <td>{p.email}</td>
                                        <td>{p.age}</td>
                                        <td>{p.gender}</td>
                                        <td>{p.last_treatment}</td>
                                        <td>
                                            <div className="action-group">
                                                <button className="btn secondary sm" onClick={() => handleEdit(p)}>Edit</button>
                                                <button className="btn danger sm" onClick={() => setPendingDeleteId(p.id)}>Delete</button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="empty-state">
                        <h3>No patients found.</h3>
                        <p>Add your first patient.</p>
                        <button className="btn" type="button" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>Add patient</button>
                    </div>
                )}
            </section>

            <ConfirmModal
                open={Boolean(pendingDeleteId)}
                title="Delete this patient?"
                message="This will permanently remove the patient record. This action cannot be undone."
                confirmLabel="Delete"
                onConfirm={() => void handleDeleteConfirm()}
                onCancel={() => setPendingDeleteId(null)}
            />
        </div>
    );
}

export default Patients;