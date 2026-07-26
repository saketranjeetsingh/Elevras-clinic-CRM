import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { get, post, put, del } from "../services/api";

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
        address: "",
        blood_group: "",
        medical_history: "",
        notes: "",
        last_treatment: "",
    });
    const [editingId, setEditingId] = useState(null);
    const [success, setSuccess] = useState(null);
    const [searchQuery, setSearchQuery] = useState("");

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
        setSuccess(null);

        if (!form.name.trim() || !form.phone.trim() || !form.email.trim()) {
            setError("Please enter the patient name, phone number, and email.");
            return;
        }

        try {
            if (editingId) {
                await put(`/patients/${editingId}`, {
                    name: form.name,
                    phone: form.phone,
                    email: form.email,
                    age: Number(form.age) || 0,
                    gender: form.gender,
                    address: form.address,
                    blood_group: form.blood_group,
                    medical_history: form.medical_history,
                    notes: form.notes,
                    last_treatment: form.last_treatment,
                });

                setSuccess("Patient updated successfully");
                setEditingId(null);
            } else {
                await post("/patients", {
                    name: form.name,
                    phone: form.phone,
                    email: form.email,
                    age: Number(form.age) || 0,
                    gender: form.gender,
                    address: form.address,
                    blood_group: form.blood_group,
                    medical_history: form.medical_history,
                    notes: form.notes,
                    last_treatment: form.last_treatment,
                });

                setSuccess("Patient created successfully");
            }

            setForm({
                name: "",
                phone: "",
                email: "",
                age: "",
                gender: "",
                address: "",
                blood_group: "",
                medical_history: "",
                notes: "",
                last_treatment: "",
            });

            await fetchPatients();
        } catch (err) {
            setSuccess(null);
            setError(err?.detail || err?.message || "We could not save the patient record.");
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
            address: patient.address || "",
            blood_group: patient.blood_group || "",
            medical_history: patient.medical_history || "",
            notes: patient.notes || "",
            last_treatment: patient.last_treatment || "",
        });
        setSuccess(null);
        setError(null);
    };

    const handleDelete = async (id) => {
        if (!window.confirm("Are you sure you want to delete this patient?")) return;
        setError(null);
        setSuccess(null);

        try {
            await del(`/patients/${id}`);
            setSuccess("Patient deleted successfully");
            await fetchPatients();
        } catch (err) {
            setError(err?.detail || err?.message || "We could not delete the patient record.");
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
                patient.last_treatment,
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
                    <input name="name" placeholder="Name" value={form.name} onChange={handleChange} />
                    <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
                    <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
                    <input name="age" type="number" placeholder="Age" value={form.age} onChange={handleChange} />
                    <input name="gender" placeholder="Gender" value={form.gender} onChange={handleChange} />
                    <input name="address" placeholder="Address" value={form.address} onChange={handleChange} />
                    <input name="blood_group" placeholder="Blood Group" value={form.blood_group} onChange={handleChange} />
                    <input name="medical_history" placeholder="Medical History" value={form.medical_history} onChange={handleChange} />
                    <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                    <input name="last_treatment" type="date" value={form.last_treatment} onChange={handleChange} />
                    <div className="full-width action-row">
                        <button className="btn" type="submit">{editingId ? "Save changes" : "Create patient"}</button>
                        {editingId && <button type="button" className="btn secondary" onClick={() => { setEditingId(null); setForm({ name: "", phone: "", email: "", age: "", gender: "", address: "", blood_group: "", medical_history: "", notes: "", last_treatment: "" }); }}>Cancel</button>}
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

            {success && <div className="status-card status-card-success"><span>{success}</span></div>}
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
                                        </td>
                                        <td>{p.phone}</td>
                                        <td>{p.email}</td>
                                        <td>{p.age}</td>
                                        <td>{p.gender}</td>
                                        <td>{p.last_treatment}</td>
                                        <td>
                                            <div className="action-group">
                                                <button className="btn secondary" onClick={() => handleEdit(p)}>Edit</button>
                                                <button className="btn danger" onClick={() => handleDelete(p.id)}>Delete</button>
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
        </div>
    );
}

export default Patients;
