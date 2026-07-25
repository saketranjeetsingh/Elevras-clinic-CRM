function PatientSummaryCard({ patient }) {
    if (!patient) {
        return null;
    }

    return (
        <div className="patient-summary-card">
            <div className="field-label">Selected patient</div>
            <div className="patient-summary-row">
                <strong>{patient.name || "Patient"}</strong>
                <span>{patient.age ? `${patient.age} yrs` : "Age not provided"}</span>
            </div>
            <div className="patient-summary-row">
                <span>{patient.gender || "Gender not provided"}</span>
                <span>{patient.phone || "No phone provided"}</span>
            </div>
        </div>
    );
}

export default PatientSummaryCard;
