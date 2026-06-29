import { useEffect, useState } from "react";
import { get, post, put, del } from "../services/api";

function Patients() {
    const [patients, setPatients] = useState([]);
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
    const [searchName, setSearchName] = useState("");
    const [searchPhone, setSearchPhone] = useState("");

    const fetchPatients = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await get("/patients");
            setPatients(data || []);
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
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
            setError(err?.detail || err?.message || JSON.stringify(err));
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
        if (!window.confirm("Delete patient?")) return;
        setError(null);
        setSuccess(null);

        try {
            await del(`/patients/${id}`);
            setSuccess("Patient deleted successfully");
            await fetchPatients();
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    const handleSearchByName = async () => {
        if (!searchName) return fetchPatients();
        setLoading(true);
        setError(null);
        try {
            const data = await get(`/patients/search/name/${encodeURIComponent(searchName)}`);
            setPatients(data || []);
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        } finally {
            setLoading(false);
        }
    };

    const handleSearchByPhone = async () => {
        if (!searchPhone) return fetchPatients();
        setLoading(true);
        setError(null);
        try {
            const data = await get(`/patients/search/phone/${encodeURIComponent(searchPhone)}`);
            setPatients(data ? [data] : []);
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page">
            <h1>Patients</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <input name="name" placeholder="Name" value={form.name} onChange={handleChange} />
                <input name="phone" placeholder="Phone" value={form.phone} onChange={handleChange} />
                <input name="email" placeholder="Email" value={form.email} onChange={handleChange} />
                <input name="age" placeholder="Age" value={form.age} onChange={handleChange} />
                <input name="gender" placeholder="Gender" value={form.gender} onChange={handleChange} />
                <input name="notes" placeholder="Notes" value={form.notes} onChange={handleChange} />
                <input name="last_treatment" placeholder="Last Treatment" value={form.last_treatment} onChange={handleChange} />
                <button className="btn" type="submit">{editingId ? "Save" : "Create"}</button>
                {editingId && <button type="button" className="btn" onClick={() => { setEditingId(null); setForm({ name: "", phone: "", email: "", age: "", gender: "", notes: "", last_treatment: "" }); }}>Cancel</button>}
            </form>

            <div style={{ marginBottom: 12 }}>
                <input placeholder="Search name" value={searchName} onChange={(e) => setSearchName(e.target.value)} />
                <button className="btn" onClick={handleSearchByName}>Search Name</button>
                <input placeholder="Search phone" value={searchPhone} onChange={(e) => setSearchPhone(e.target.value)} style={{ marginLeft: 8 }} />
                <button className="btn" onClick={handleSearchByPhone}>Search Phone</button>
                <button className="btn" onClick={fetchPatients} style={{ marginLeft: 8 }}>Clear</button>
            </div>

            {success && <p className="success">{success}</p>}

            {loading && <p>Loading patients...</p>}
            {error && <p className="error">Error: {error}</p>}

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
