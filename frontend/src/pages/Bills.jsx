import { useEffect, useState } from "react";
import { get, post, put } from "../services/api";

function Bills() {
    const [bills, setBills] = useState([]);
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    const [form, setForm] = useState({
        patient_id: "",
        amount: "",
        payment_status: "Pending",
        payment_method: "Cash",
    });

    const fetchBills = async () => {
        setLoading(true);
        setError(null);
        try {
            const [billsData, patientsData] = await Promise.all([
                get("/bills"),
                get("/patients"),
            ]);
            setBills(billsData || []);
            setPatients(patientsData || []);
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
        setError(null);
        setSuccess(null);
        try {
            await post("/bills", {
                patient_id: Number(form.patient_id),
                amount: Number(form.amount) || 0,
                payment_status: form.payment_status,
                payment_method: form.payment_method,
            });

            setForm({ patient_id: "", amount: "", payment_status: "Pending", payment_method: "Cash" });
            await fetchBills();
            setSuccess("Bill created successfully");
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    const handleUpdatePaymentStatus = async (bill, nextStatus) => {
        setError(null);
        setSuccess(null);
        try {
            await put(`/bills/${bill.id}`, null, { payment_status: nextStatus });
            await fetchBills();
            setSuccess("Bill updated successfully");
        } catch (err) {
            setError(err?.detail || err?.message || JSON.stringify(err));
        }
    };

    return (
        <div className="page">
            <h1>Bills</h1>

            <form onSubmit={handleCreate} className="form-row" style={{ marginBottom: 12 }}>
                <select name="patient_id" value={form.patient_id} onChange={handleChange}>
                    <option value="">Select patient</option>
                    {patients.map((patient) => (
                        <option key={patient.id} value={patient.id}>{patient.name} ({patient.phone})</option>
                    ))}
                </select>
                <input name="amount" placeholder="Amount" value={form.amount} onChange={handleChange} />
                <select name="payment_status" value={form.payment_status} onChange={handleChange}>
                    <option value="Pending">Pending</option>
                    <option value="Paid">Paid</option>
                    <option value="Overdue">Overdue</option>
                </select>
                <select name="payment_method" value={form.payment_method} onChange={handleChange}>
                    <option value="Cash">Cash</option>
                    <option value="Card">Card</option>
                    <option value="Insurance">Insurance</option>
                </select>
                <button className="btn" type="submit">Create</button>
            </form>

            {success && <p className="success">{success}</p>}
            {loading && <p>Loading bills...</p>}
            {error && <p className="error">Error: {error}</p>}

            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient</th>
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
                                <select value={b.payment_status || "Pending"} onChange={(e) => handleUpdatePaymentStatus(b, e.target.value)}>
                                    <option value="Pending">Pending</option>
                                    <option value="Paid">Paid</option>
                                    <option value="Overdue">Overdue</option>
                                </select>
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

