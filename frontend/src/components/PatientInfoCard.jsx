function PatientInfoCard({ patient }) {
    return (
        <section className="card profile-card">
            <div className="section-heading-row">
                <h2>Patient Information</h2>
                <span className="muted-chip">ID #{patient?.id}</span>
            </div>

            <div className="info-grid">
                <div><span className="field-label">Name</span><p>{patient?.name || "—"}</p></div>
                <div><span className="field-label">Age</span><p>{patient?.age || "—"}</p></div>
                <div><span className="field-label">Gender</span><p>{patient?.gender || "—"}</p></div>
                <div><span className="field-label">Phone</span><p>{patient?.phone || "—"}</p></div>
                <div><span className="field-label">Email</span><p>{patient?.email || "—"}</p></div>
                <div><span className="field-label">Address</span><p>{patient?.address || "—"}</p></div>
                <div><span className="field-label">Blood Group</span><p>{patient?.blood_group || "—"}</p></div>
                <div><span className="field-label">Last Treatment Date</span><p>{patient?.last_treatment || "—"}</p></div>
            </div>
        </section>
    );
}

export default PatientInfoCard;
