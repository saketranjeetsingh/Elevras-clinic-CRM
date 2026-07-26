import { useContext, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import AuthContext from "../contexts/AuthContext";
import Icon from "../components/Icon";
import { get } from "../services/api";

const emptyStats = {
    total_patients: 0,
    total_appointments: 0,
    total_treatments: 0,
    total_bills: 0,
    total_revenue: 0,
};

function formatDateLabel(value) {
    if (!value) {
        return "No date";
    }

    const parsedDate = new Date(value);
    if (Number.isNaN(parsedDate.getTime())) {
        return value;
    }

    return new Intl.DateTimeFormat("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
    }).format(parsedDate);
}

function isSameDay(value, referenceDate) {
    const parsedDate = new Date(value);
    if (Number.isNaN(parsedDate.getTime())) {
        return false;
    }

    return (
        parsedDate.getFullYear() === referenceDate.getFullYear() &&
        parsedDate.getMonth() === referenceDate.getMonth() &&
        parsedDate.getDate() === referenceDate.getDate()
    );
}

function isUpcoming(value) {
    const parsedDate = new Date(value);
    if (Number.isNaN(parsedDate.getTime())) {
        return false;
    }

    const startOfToday = new Date();
    startOfToday.setHours(0, 0, 0, 0);
    return parsedDate.getTime() >= startOfToday.getTime();
}

function Dashboard() {
    const { user } = useContext(AuthContext);
    const [stats, setStats] = useState(emptyStats);
    const [appointments, setAppointments] = useState([]);
    const [patients, setPatients] = useState([]);
    const [treatments, setTreatments] = useState([]);
    const [bills, setBills] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            setLoading(true);
            setError(null);
            try {
                const [statsData, appointmentsData, patientsData, treatmentsData, billsData] = await Promise.all([
                    get("/dashboard/stats"),
                    get("/appointments"),
                    get("/patients"),
                    get("/treatments"),
                    get("/bills"),
                ]);

                setStats({
                    ...emptyStats,
                    ...(statsData || {}),
                });
                setAppointments(appointmentsData || []);
                setPatients(patientsData || []);
                setTreatments(treatmentsData || []);
                setBills(billsData || []);
            } catch (err) {
                setStats(emptyStats);
                setAppointments([]);
                setPatients([]);
                setTreatments([]);
                setBills([]);
                setError(err?.detail || err?.message || "Unable to load dashboard. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    const greetingName = user?.doctor_name || user?.name || "Doctor";
    const displayName = greetingName.startsWith("Dr.") ? greetingName : `Dr. ${greetingName}`;
    const hour = new Date().getHours();
    const greeting = hour < 12 ? "Good Morning" : hour < 17 ? "Good Afternoon" : "Good Evening";

    const patientLookup = useMemo(() => new Map(patients.map((patient) => [patient.id, patient])), [patients]);

    const todayAppointments = useMemo(() => {
        const today = new Date();
        return [...appointments]
            .filter((appointment) => isSameDay(appointment.appointment_date, today))
            .sort((first, second) => (first.appointment_date || "").localeCompare(second.appointment_date || ""));
    }, [appointments]);

    const pendingBills = useMemo(() => {
        return [...bills].filter((bill) => {
            const status = String(bill.payment_status || "Pending").toLowerCase();
            return status === "pending" || status === "overdue";
        });
    }, [bills]);

    const activeTreatments = useMemo(() => {
        return [...treatments].filter((treatment) => String(treatment.status || "").toLowerCase() !== "completed");
    }, [treatments]);

    const recentPatients = useMemo(() => {
        return [...patients]
            .sort((first, second) => (Number(second.id) || 0) - (Number(first.id) || 0))
            .slice(0, 5);
    }, [patients]);

    const upcomingFollowUps = useMemo(() => {
        return [...appointments]
            .filter((appointment) => {
                const status = String(appointment.status || "Scheduled").toLowerCase();
                return isUpcoming(appointment.appointment_date) && status !== "cancelled" && status !== "completed";
            })
            .sort((first, second) => (first.appointment_date || "").localeCompare(second.appointment_date || ""))
            .slice(0, 3);
    }, [appointments]);

    const recentActivity = useMemo(() => {
        const activityItems = [
            ...appointments.map((appointment) => ({
                id: `appointment-${appointment.id}`,
                patientId: appointment.patient_id,
                event: `Appointment ${appointment.status || "Scheduled"}`,
                date: appointment.appointment_date || "Recently added",
            })),
            ...treatments.map((treatment) => ({
                id: `treatment-${treatment.id}`,
                patientId: treatment.patient_id,
                event: `${treatment.treatment_name || "Treatment"} • ${treatment.status || "Planned"}`,
                date: patientLookup.get(treatment.patient_id)?.last_treatment || "Recently added",
            })),
            ...bills.map((bill) => ({
                id: `bill-${bill.id}`,
                patientId: bill.patient_id,
                event: `Bill • ${bill.payment_status || "Pending"}`,
                date: patientLookup.get(bill.patient_id)?.last_treatment || "Recently added",
            })),
        ];

        return activityItems
            .sort((first, second) => (second.date || "").localeCompare(first.date || ""))
            .slice(0, 5);
    }, [appointments, bills, patientLookup, treatments]);

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow"><Icon name="dashboard" size={14} /> Welcome back</p>
                    <h1>{greeting}, {displayName}</h1>
                    <p className="page-subtitle">{user?.clinic_name || "Your Clinic"}</p>
                </div>
            </div>

            {error && (
                <div className="status-card status-card-error">
                    <Icon name="alert" size={18} />
                    <span>{error}</span>
                </div>
            )}

            {loading ? (
                <div className="dashboard-loading">
                    <div className="skeleton-card skeleton-hero" />
                    <div className="stats-grid">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <div className="skeleton-card" key={index} />
                        ))}
                    </div>
                    <div className="dashboard-grid">
                        <div className="skeleton-card skeleton-large" />
                        <div className="skeleton-card skeleton-large" />
                    </div>
                </div>
            ) : (
                <>
                    <div className="stats-grid">
                        <div className="card stat-card">
                            <div className="stat-card-top">
                                <span className="stat-icon"><Icon name="calendar" /></span>
                                <span className="muted-chip">Today</span>
                            </div>
                            <h3>Today's Appointments</h3>
                            <p>{todayAppointments.length}</p>
                            <div className="stat-footnote">Scheduled for today</div>
                        </div>

                        <div className="card stat-card">
                            <div className="stat-card-top">
                                <span className="stat-icon"><Icon name="patients" /></span>
                                <span className="muted-chip">Patients</span>
                            </div>
                            <h3>Total Patients</h3>
                            <p>{stats.total_patients}</p>
                            <div className="stat-footnote">Active patient list</div>
                        </div>

                        <div className="card stat-card">
                            <div className="stat-card-top">
                                <span className="stat-icon"><Icon name="bills" /></span>
                                <span className="muted-chip">Billing</span>
                            </div>
                            <h3>Pending Bills</h3>
                            <p>{pendingBills.length}</p>
                            <div className="stat-footnote">Needs follow-up</div>
                        </div>

                        <div className="card stat-card">
                            <div className="stat-card-top">
                                <span className="stat-icon"><Icon name="treatments" /></span>
                                <span className="muted-chip">Care plan</span>
                            </div>
                            <h3>Active Treatments</h3>
                            <p>{activeTreatments.length}</p>
                            <div className="stat-footnote">In progress</div>
                        </div>
                    </div>

                    <div className="dashboard-grid">
                        <section className="section-card">
                            <div className="section-heading-row">
                                <h2><Icon name="patients" size={18} /> Recent Patients</h2>
                                <Link to="/patients" className="section-link">Manage patients</Link>
                            </div>
                            {recentPatients.length > 0 ? (
                                <ul className="stack-list">
                                    {recentPatients.map((patient) => (
                                        <li key={patient.id}>
                                            <Link to={`/patients/${patient.id}`} className="list-link">
                                                <div>
                                                    <div className="list-item-title">{patient.name}</div>
                                                    <div className="list-item-subtitle">{patient.phone || "No phone on file"}</div>
                                                </div>
                                                <div className="list-item-meta">
                                                    {patient.last_treatment ? formatDateLabel(patient.last_treatment) : "No treatment yet"}
                                                </div>
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty-state compact-empty">
                                    <p>No patients added yet.</p>
                                    <Link to="/patients" className="btn">Add your first patient</Link>
                                </div>
                            )}
                        </section>

                        <section className="section-card">
                            <div className="section-heading-row">
                                <h2><Icon name="activity" size={18} /> Recent Activity</h2>
                                <span className="muted-chip">Latest updates</span>
                            </div>
                            {recentActivity.length > 0 ? (
                                <ul className="stack-list">
                                    {recentActivity.map((item) => {
                                        const patient = patientLookup.get(item.patientId);
                                        return (
                                            <li key={item.id} className="activity-list-item">
                                                <div>
                                                    <div className="list-item-title">{patient?.name || "Unknown patient"}</div>
                                                    <div className="list-item-subtitle">{item.event}</div>
                                                </div>
                                                <div className="list-item-meta">{formatDateLabel(item.date)}</div>
                                            </li>
                                        );
                                    })}
                                </ul>
                            ) : (
                                <div className="empty-state compact-empty">
                                    <p>No recent activity yet.</p>
                                </div>
                            )}
                        </section>

                        <section className="section-card dashboard-span">
                            <div className="section-heading-row">
                                <h2><Icon name="followup" size={18} /> Upcoming Follow-ups</h2>
                                <span className="muted-chip">Scheduled</span>
                            </div>
                            {upcomingFollowUps.length > 0 ? (
                                <ul className="stack-list">
                                    {upcomingFollowUps.map((appointment) => (
                                        <li key={appointment.id} className="activity-list-item">
                                            <div>
                                                <div className="list-item-title">{patientLookup.get(appointment.patient_id)?.name || "Unknown patient"}</div>
                                                <div className="list-item-subtitle">{appointment.notes || "Follow-up scheduled"}</div>
                                            </div>
                                            <div className="list-item-meta">{formatDateLabel(appointment.appointment_date)}</div>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty-state compact-empty">
                                    <p>No follow-ups scheduled.</p>
                                </div>
                            )}
                        </section>
                    </div>
                </>
            )}
        </div>
    );
}

export default Dashboard;