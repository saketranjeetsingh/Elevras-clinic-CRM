import { Link } from "react-router-dom";

function PatientHeader({ patient }) {
    return (
        <div className="page-header">
            <Link to="/patients" className="back-link">← Back to Patients</Link>
            <div className="eyebrow">Patient profile</div>
            <h1>{patient?.name || "Patient"}</h1>
            <p className="page-subtitle">Complete medical record, visit history, and fast actions</p>
        </div>
    );
}

export default PatientHeader;
