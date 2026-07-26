import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { get } from "../services/api";

function PatientSelector({ selectedPatient, onSelect, onClear }) {
    const [patients, setPatients] = useState([]);
    const [searchText, setSearchText] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();
    const wrapperRef = useRef(null);

    useEffect(() => {
        const fetchPatients = async () => {
            setLoading(true);
            setError(null);
            try {
                const data = await get("/patients");
                setPatients(data || []);
            } catch (err) {
                setError(err?.detail || err?.message || "We could not load patients.");
            } finally {
                setLoading(false);
            }
        };

        const timer = window.setTimeout(() => {
            void fetchPatients();
        }, 0);

        return () => window.clearTimeout(timer);
    }, []);

    const selectedLabel = selectedPatient
        ? `${selectedPatient.name || "Patient"} • ${selectedPatient.phone || "No phone provided"}`
        : "";
    const inputValue = selectedPatient ? selectedLabel : searchText;

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const filteredPatients = useMemo(() => {
        const normalizedQuery = inputValue.trim().toLowerCase();
        if (!normalizedQuery) {
            return patients;
        }

        return patients.filter((patient) => {
            const name = (patient.name || "").toLowerCase();
            const phone = (patient.phone || "").toLowerCase();
            return name.includes(normalizedQuery) || phone.includes(normalizedQuery);
        });
    }, [inputValue, patients]);

    const handleSelect = (patient) => {
        onSelect?.(patient);
        setSearchText(`${patient.name || "Patient"} • ${patient.phone || "No phone provided"}`);
        setIsOpen(false);
    };

    const handleClear = () => {
        setSearchText("");
        setIsOpen(false);
        onClear?.();
    };

    const showSelectionHint = Boolean(inputValue.trim()) && !selectedPatient;

    return (
        <div className="patient-selector" ref={wrapperRef}>
            <label className="field-label">Patient</label>
            <div className="patient-selector-input-wrap">
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => {
                        setSearchText(e.target.value);
                        setIsOpen(true);
                    }}
                    onFocus={() => setIsOpen(true)}
                    placeholder="Search by name or phone"
                />
                {selectedPatient && (
                    <button className="patient-selector-clear" type="button" onClick={handleClear}>
                        Clear
                    </button>
                )}
            </div>

            {loading && <p className="status-message">Loading patients...</p>}
            {showSelectionHint && <p className="patient-selector-helper">Select a patient from the list.</p>}
            {error && <p className="status-message error">{error}</p>}

            {!loading && !error && patients.length === 0 && (
                <div className="patient-selector-empty">
                    <p>No patients found.</p>
                    <p>Please create a patient first.</p>
                    <button className="btn" type="button" onClick={() => navigate("/patients")}>
                        Go to Patients
                    </button>
                </div>
            )}

            {isOpen && !loading && !error && patients.length > 0 && (
                <div className="patient-selector-list" role="listbox">
                    {filteredPatients.length > 0 ? (
                        filteredPatients.map((patient) => (
                            <button
                                key={patient.id}
                                className={`patient-selector-option ${selectedPatient?.id === patient.id ? "is-selected" : ""}`}
                                type="button"
                                onClick={() => handleSelect(patient)}
                            >
                                <span className="patient-selector-option-name">{patient.name || "Unnamed patient"}</span>
                                <span className="patient-selector-option-phone">{patient.phone || "No phone provided"}</span>
                            </button>
                        ))
                    ) : (
                        <div className="patient-selector-option empty">No patient matches your search.</div>
                    )}
                </div>
            )}
        </div>
    );
}

export default PatientSelector;
