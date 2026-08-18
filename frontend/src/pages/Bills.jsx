import { useEffect, useMemo, useState } from "react";
import PatientSelector from "../components/PatientSelector";
import PatientSummaryCard from "../components/PatientSummaryCard";
import { get, post, put } from "../services/api";
import { createPatientLookup } from "../utils/patientHelpers";
import { useToast } from "../components/ToastContext";

function Bills() {
    const [bills, setBills] = useState([]);
    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const toast = useToast();

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
            toast.error(err?.detail || err?.message || "We could not load bills right now.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchBills();
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

        if (!selectedPatient) {
            toast.error("Please select a patient before creating a bill.");
            return;
        }

        if (!form.amount || Number(form.amount) <= 0) {
            toast.error("Please enter a valid bill amount.");
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
            toast.success("Bill created successfully");
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not save the bill.");
        }
    };

    const handleUpdatePaymentStatus = async (bill, nextStatus) => {
        setError(null);
        try {
            await put(`/bills/${bill.id}`, { payment_status: nextStatus });
            await fetchBills();
            toast.success("Bill updated successfully");
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not update the bill.");
        }
    };

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow"><span className="eyebrow-icon"><svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor" aria-hidden="true"><path d="M4 5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v14l-3-2-3 2-3-2-3 2-3-2Zm4 3h8v2H8Zm0 4h8v2H8Z" /></svg></span> Bills</p>
                    <h1>Stay on top of payments</h1>
                    <p className="page-subtitle">Create, review, and update invoices with a more structured workflow.</p>
                </div>
            </div>

            <section className="section-card form-card">
                <div className="section-heading-row">
                    <h2>Create bill</h2>
                    <span className="muted-chip">Invoice entry</span>
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
                            onQuickAdd={() => void fetchBills()}
                        />
                    </div>
                    <div className="form-field">
                        <label htmlFor="bill-amount">Amount</label>
                        <input id="bill-amount" name="amount" type="number" min="0" placeholder="Amount" value={form.amount} onChange={handleChange} />
                    </div>
                    <div className="form-field">
                        <label htmlFor="bill-payment-status">Payment status</label>
                        <select id="bill-payment-status" name="payment_status" value={form.payment_status} onChange={handleChange}>
                            <option value="Pending">Pending</option>
                            <option value="Paid">Paid</option>
                            <option value="Overdue">Overdue</option>
                        </select>
                    </div>
                    <div className="form-field">
                        <label htmlFor="bill-payment-method">Payment method</label>
                        <select id="bill-payment-method" name="payment_method" value={form.payment_method} onChange={handleChange}>
                            <option value="Cash">Cash</option>
                            <option value="Card">Card</option>
                            <option value="Insurance">Insurance</option>
                        </select>
                    </div>
                    <div className="full-width action-row">
                        <button className="btn" type="submit" disabled={!selectedPatient}>Create bill</button>
                    </div>
                </form>
            </section>

            <PatientSummaryCard patient={selectedPatient} />

            {error && <div className="status-card status-card-error"><span>{error}</span></div>}

            <section className="section-card">
                <div className="section-heading-row">
                    <h2>Billing ledger</h2>
                    <span className="muted-chip">{bills.length} entries</span>
                </div>
                {loading ? (
                    <div className="table-skeleton">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <div className="skeleton-row" key={index} />
                        ))}
                    </div>
                ) : bills.length > 0 ? (
                    <div className="table-wrap">
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
                ) : (
                    <div className="empty-state">
                        <h3>No bills generated.</h3>
                        <p>Generate your first bill.</p>
                    </div>
                )}
            </section>
        </div>
    );
}

export default Bills;