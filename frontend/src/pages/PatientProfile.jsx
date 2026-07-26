import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { get, post } from "../services/api";
import PatientHeader from "../components/PatientHeader";
import PatientInfoCard from "../components/PatientInfoCard";
import MedicalHistoryCard from "../components/MedicalHistoryCard";
import RecentActivity from "../components/RecentActivity";
import PatientTimeline from "../components/PatientTimeline";
import ProfileStats from "../components/ProfileStats";
import HistoryTables from "../components/HistoryTables";
import QuickActions from "../components/QuickActions";

function formatCurrency(value) {
    const amount = Number(value || 0);
    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
    }).format(amount);
}

function formatDateLabel(value) {
    if (!value) {
        return "Date pending";
    }

    const parsedDate = new Date(value);
    if (Number.isNaN(parsedDate.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("en-US", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(parsedDate);
}

function statusBadgeClass(status) {
    const normalized = String(status || "").toLowerCase();

    if (normalized.includes("paid") || normalized.includes("completed") || normalized.includes("done")) {
        return "status-badge success";
    }

    if (normalized.includes("cancel") || normalized.includes("overdue")) {
        return "status-badge danger";
    }

    return "status-badge neutral";
}

function getMedicalHistoryItems(value) {
    const text = String(value || "").trim();

    if (!text) {
        return [];
    }

    return text
        .split(/[\n,]+/)
        .map((item) => item.trim())
        .filter(Boolean);
}

function PatientProfile() {
    const { id } = useParams();
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [actionMessage, setActionMessage] = useState(null);
    const [activeAction, setActiveAction] = useState(null);
    const [quickForm, setQuickForm] = useState({
        appointment: { doctor_name: "", appointment_date: "", status: "Scheduled", notes: "" },
        treatment: { treatment_name: "", cost: "", status: "Planned", notes: "" },
        bill: { amount: "", payment_status: "Pending", payment_method: "Cash" },
    });

    const fetchProfile = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const data = await get(`/patients/${id}/profile`);
            setProfile(data || null);
        } catch (err) {
            setError(err?.detail || err?.message || "We could not load the patient profile.");
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        if (id) {
            const timer = window.setTimeout(() => {
                void fetchProfile();
            }, 0);

            return () => window.clearTimeout(timer);
        }
    }, [fetchProfile, id]);

    const patient = profile?.patient || {};
    const appointments = profile?.appointments || [];
    const treatments = profile?.treatments || [];
    const bills = profile?.bills || [];
    const stats = profile?.stats || {};

    const medicalHistoryItems = getMedicalHistoryItems(patient.medical_history);

    const timelineItems = [
        ...appointments.map((appointment) => ({
            id: `appointment-${appointment.id}`,
            type: "appointment",
            icon: "🗓️",
            date: appointment.appointment_date || "",
            title: "Appointment",
            description: appointment.status ? `${appointment.status}` : "Appointment created",
            badge: appointment.status || "Scheduled",
        })),
        ...treatments.map((treatment) => ({
            id: `treatment-${treatment.id}`,
            type: "treatment",
            icon: "💊",
            date: "",
            title: "Treatment Added",
            description: treatment.treatment_name || "Treatment recorded",
            badge: treatment.status || "Planned",
        })),
        ...bills.map((bill) => ({
            id: `bill-${bill.id}`,
            type: "bill",
            icon: "💳",
            date: "",
            title: "Bill Generated",
            description: `${formatCurrency(bill.amount)} • ${bill.payment_status || "Pending"}`,
            badge: bill.payment_status || "Pending",
        })),
    ].sort((first, second) => {
        const firstDate = first.date ? new Date(first.date).getTime() : Number.POSITIVE_INFINITY;
        const secondDate = second.date ? new Date(second.date).getTime() : Number.POSITIVE_INFINITY;

        if (firstDate !== secondDate) {
            return firstDate - secondDate;
        }

        return first.id.localeCompare(second.id);
    });

    const lastAppointment = [...appointments].sort((first, second) => (second.id || 0) - (first.id || 0))[0];
    const lastTreatment = [...treatments].sort((first, second) => (second.id || 0) - (first.id || 0))[0];
    const lastBill = [...bills].sort((first, second) => (second.id || 0) - (first.id || 0))[0];

    const handleQuickFormChange = (section, event) => {
        const { name, value } = event.target;
        setQuickForm((current) => ({
            ...current,
            [section]: {
                ...current[section],
                [name]: value,
            },
        }));
    };

    const handleQuickActionSubmit = async (event) => {
        event.preventDefault();
        setError(null);
        setActionMessage(null);

        try {
            if (activeAction === "appointment") {
                await post("/appointments", {
                    patient_id: Number(patient.id),
                    doctor_name: quickForm.appointment.doctor_name,
                    appointment_date: quickForm.appointment.appointment_date,
                    status: quickForm.appointment.status,
                    notes: quickForm.appointment.notes,
                });
                setActionMessage("Appointment created successfully.");
            } else if (activeAction === "treatment") {
                await post("/treatments", {
                    patient_id: Number(patient.id),
                    treatment_name: quickForm.treatment.treatment_name,
                    cost: Number(quickForm.treatment.cost) || 0,
                    status: quickForm.treatment.status,
                    notes: quickForm.treatment.notes,
                });
                setActionMessage("Treatment created successfully.");
            } else if (activeAction === "bill") {
                await post("/bills", {
                    patient_id: Number(patient.id),
                    amount: Number(quickForm.bill.amount) || 0,
                    payment_status: quickForm.bill.payment_status,
                    payment_method: quickForm.bill.payment_method,
                });
                setActionMessage("Bill generated successfully.");
            }

            setActiveAction(null);
            setQuickForm({
                appointment: { doctor_name: "", appointment_date: "", status: "Scheduled", notes: "" },
                treatment: { treatment_name: "", cost: "", status: "Planned", notes: "" },
                bill: { amount: "", payment_status: "Pending", payment_method: "Cash" },
            });
            await fetchProfile();
        } catch (err) {
            setError(err?.detail || err?.message || "We could not save the new record.");
        }
    };

    return (
        <div className="page">
            <PatientHeader patient={patient} />

            {actionMessage && <p className="status-message success">{actionMessage}</p>}
            {loading && <p className="status-message">Loading patient profile...</p>}
            {error && <p className="status-message error">{error}</p>}

            {!loading && !error && profile && (
                <div className="profile-layout">
                    <PatientInfoCard patient={patient} />

                    <QuickActions
                        activeAction={activeAction}
                        onSelectAction={setActiveAction}
                        onCancel={() => setActiveAction(null)}
                        onSubmit={handleQuickActionSubmit}
                        onFieldChange={handleQuickFormChange}
                        quickForm={quickForm}
                    />

                    <ProfileStats stats={stats} formatCurrency={formatCurrency} />

                    <RecentActivity
                        lastAppointment={lastAppointment}
                        lastTreatment={lastTreatment}
                        lastBill={lastBill}
                        formatDateLabel={formatDateLabel}
                        statusBadgeClass={statusBadgeClass}
                        formatCurrency={formatCurrency}
                    />

                    <MedicalHistoryCard medicalHistoryItems={medicalHistoryItems} />

                    <PatientTimeline timelineItems={timelineItems} formatDateLabel={formatDateLabel} />

                    <HistoryTables
                        appointments={appointments}
                        treatments={treatments}
                        bills={bills}
                        formatCurrency={formatCurrency}
                        statusBadgeClass={statusBadgeClass}
                    />
                </div>
            )}
        </div>
    );
}

export default PatientProfile;
