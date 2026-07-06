import { useEffect, useState } from "react";
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
        fetchPatients();
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
            <h1>Patients</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <input name="name" placeholder="Name" value={form.name} onChange={handleChange} />
                <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
                <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
                <input name="age" type="number" placeholder="Age" value={form.age} onChange={handleChange} />
                <input name="gender" placeholder="Gender" value={form.gender} onChange={handleChange} />
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <input name="last_treatment" type="date" value={form.last_treatment} onChange={handleChange} />
                <button className="btn" type="submit">{editingId ? "Save" : "Create"}</button>
                {editingId && <button type="button" className="btn" onClick={() => { setEditingId(null); setForm({ name: "", phone: "", email: "", age: "", gender: "", notes: "", last_treatment: "" }); }}>Cancel</button>}
            </form>

            <form onSubmit={handleSearch} className="search-row" style={{ marginBottom: 12 }}>
                <input placeholder="Search by name, phone, email, or treatment" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
                <button className="btn" type="submit">Search</button>
                <button className="btn" type="button" onClick={() => { setSearchQuery(""); setPatients(allPatients); }} style={{ marginLeft: 8 }}>Clear</button>
            </form>

            {success && <p className="status-message success">{success}</p>}
            {loading && <p className="status-message">Loading patients...</p>}
            {error && <p className="status-message error">{error}</p>}

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
                            <td>{p.id}</td>
                            <td>{p.name}</td>
                            <td>{p.phone}</td>
                            <td>{p.email}</td>
                            <td>{p.age}</td>
                            <td>{p.gender}</td>
                            <td>{p.last_treatment}</td>
                            <td>
                                <button className="btn" onClick={() => handleEdit(p)}>Edit</button>
                                <button className="btn" onClick={() => handleDelete(p.id)} style={{ marginLeft: 6 }}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Patients;
