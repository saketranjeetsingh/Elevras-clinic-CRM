import { useEffect, useState } from "react";
import { get, post, put } from "../services/api";

function Bills() {
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        amount: "",
        payment_status: "",
        payment_method: "",
    });

    const fetchBills = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await get("/bills");
            setBills(data || []);
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBills();
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await post("/bills", {
                patient_id: Number(form.patient_id),
                amount: Number(form.amount) || 0,
                payment_status: form.payment_status,
                payment_method: form.payment_method,
            });

            setForm({ patient_id: "", amount: "", payment_status: "", payment_method: "" });
            fetchBills();
        } catch (err) {
            alert("Failed to create bill: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    const handleUpdatePaymentStatus = async (b) => {
        const newStatus = window.prompt("New payment status", b.payment_status || "");
        if (!newStatus) return;
        try {
            await put(`/bills/${b.id}`, null, { payment_status: newStatus });
            fetchBills();
        } catch (err) {
            alert("Failed to update payment status: " + (err?.detail || err?.message || JSON.stringify(err)));
        }
    };

    return (
        <div className="page">
            <h1>Bills</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <input name="patient_id" placeholder="Patient ID" value={form.patient_id} onChange={handleChange} />
                <input name="amount" placeholder="Amount" value={form.amount} onChange={handleChange} />
                <input name="payment_status" placeholder="Payment Status" value={form.payment_status} onChange={handleChange} />
                <input name="payment_method" placeholder="Payment Method" value={form.payment_method} onChange={handleChange} />
                <button className="btn" type="submit">Create</button>
            </form>

            {loading && <p>Loading bills...</p>}
            {error && <p className="error">Error: {error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient ID</th>
                        <th>Amount</th>
                        <th>Payment Status</th>
                        <th>Payment Method</th>
                    </tr>
                </thead>
                <tbody>
                    {bills.map((b) => (
                        <tr key={b.id}>
                            <td>{b.id}</td>
                            <td>{b.patient_id}</td>
                            <td>{b.amount}</td>
                            <td>
                                {b.payment_status}
                                <button className="btn" onClick={() => handleUpdatePaymentStatus(b)} style={{ marginLeft: 6 }}>Update</button>
                            </td>
                            <td>{b.payment_method}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Bills;

