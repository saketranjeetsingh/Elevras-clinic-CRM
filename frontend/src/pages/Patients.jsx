import { useEffect, useState } from "react";
import { get, post } from "../services/api";

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
        try {
            await post("/patients", {
                name: form.name,
                phone: form.phone,
                email: form.email,
                age: Number(form.age) || 0,
                gender: form.gender,
                notes: form.notes,
                last_treatment: form.last_treatment,
            });

            setForm({
                name: "",
                phone: "",
                email: "",
                age: "",
                gender: "",
                notes: "",
                last_treatment: "",
            });

            fetchPatients();
        } catch (err) {
            alert("Failed to create patient: " + (err?.detail || err?.message || JSON.stringify(err)));
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
                <input name="last_treatment" placeholder="Last Treatment" value={form.last_treatment} onChange={handleChange} />
                <button className="btn" type="submit">Create</button>
            </form>

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
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Patients;

