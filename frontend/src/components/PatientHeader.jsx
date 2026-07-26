import { Link } from "react-router-dom";
import Icon from "./Icon";

function PatientHeader({ patient }) {
    return (
        <div className="page-header page-header-card">
            <Link to="/patients" className="back-link">← Back to Patients</Link>
            <div className="eyebrow"><Icon name="profile" size={14} /> Patient profile</div>
            <h1>{patient?.name || "Patient"}</h1>
            <p className="page-subtitle">Complete medical record, visit history, and fast actions</p>
        </div>
    );
}

export default PatientHeader;
