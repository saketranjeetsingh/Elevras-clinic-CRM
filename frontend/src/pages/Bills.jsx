import { useEffect, useMemo, useState } from "react";
import PatientSelector from "../components/PatientSelector";
import PatientSummaryCard from "../components/PatientSummaryCard";
import { get, post, put } from "../services/api";
import { createPatientLookup } from "../utils/patientHelpers";

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
    const [selectedPatient, setSelectedPatient] = useState(null);

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
            setError(err?.detail || err?.message || "We could not load bills right now.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchBills();
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
            setError("Please select a patient before creating a bill.");
            return;
        }

        try {
            await post("/bills", {
                patient_id: Number(form.patient_id),
                amount: Number(form.amount) || 0,
                payment_status: form.payment_status,
                payment_method: form.payment_method,
            });

            setForm({ patient_id: "", amount: "", payment_status: "Pending", payment_method: "Cash" });
            setSelectedPatient(null);
            await fetchBills();
            setSuccess("Bill created successfully");
        } catch (err) {
            setError(err?.detail || err?.message || "We could not save the bill.");
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
            setError(err?.detail || err?.message || "We could not update the bill.");
        }
    };

    return (
        <div className="page">
            <h1>Bills</h1>

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
                <button className="btn" type="submit" disabled={!selectedPatient}>Create</button>
            </form>

            <PatientSummaryCard patient={selectedPatient} />

            {success && <p className="status-message success">{success}</p>}
            {loading && <p className="status-message">Loading bills...</p>}
            {error && <p className="status-message error">{error}</p>}

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
                            <td>
                                <div className="patient-cell">
                                    <span>{patientLookup.get(b.patient_id)?.name || "Unknown patient"}</span>
                                    {patientLookup.get(b.patient_id)?.phone ? (
                                        <small>{patientLookup.get(b.patient_id).phone}</small>
                                    ) : null}
                                </div>
                            </td>
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

