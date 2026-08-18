import { useEffect, useMemo, useRef, useState } from "react";
import { get, post } from "../services/api";

function PatientSelector({ selectedPatient, onSelect, onClear, onQuickAdd }) {
    const [patients, setPatients] = useState([]);
    const [searchText, setSearchText] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showQuickAdd, setShowQuickAdd] = useState(false);
    const [quickAddForm, setQuickAddForm] = useState({ name: "", phone: "", email: "" });
    const [creating, setCreating] = useState(false);
    const [quickAddError, setQuickAddError] = useState(null);
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

    const openQuickAdd = (prefillName = "") => {
        setQuickAddForm((s) => ({ ...s, name: prefillName }));
        setQuickAddError(null);
        setShowQuickAdd(true);
        setIsOpen(false);
    };

    const closeQuickAdd = () => {
        setShowQuickAdd(false);
        setQuickAddError(null);
        setQuickAddForm({ name: "", phone: "", email: "" });
    };

    const handleQuickAddChange = (e) => {
        const { name, value } = e.target;
        setQuickAddForm((s) => ({ ...s, [name]: value }));
    };

    const handleQuickAddKeyDown = (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            void handleQuickAddSubmit();
        }
    };

    const handleQuickAddSubmit = async () => {
        setQuickAddError(null);
        const name = quickAddForm.name.trim();
        const phone = quickAddForm.phone.trim();

        if (!name || !phone) {
            setQuickAddError("Name and phone are required.");
            return;
        }

        setCreating(true);
        try {
            const newPatient = await post("/patients", {
                name,
                phone,
                email: quickAddForm.email.trim() || null,
            });

            setPatients((list) => [newPatient, ...list]);
            setSearchText(`${newPatient.name || "Patient"} • ${newPatient.phone || "No phone provided"}`);
            setQuickAddForm({ name: "", phone: "", email: "" });
            setShowQuickAdd(false);
            onSelect?.(newPatient);
            onQuickAdd?.(newPatient);
        } catch (err) {
            setQuickAddError(err?.detail || err?.message || "We could not create the patient.");
        } finally {
            setCreating(false);
        }
    };

    const showSelectionHint = Boolean(inputValue.trim()) && !selectedPatient;

    return (
        <div className="patient-selector" ref={wrapperRef}>
            <div className="patient-selector-label-row">
                <label className="field-label">Patient</label>
                {!selectedPatient && (
                    <button
                        className="patient-selector-new"
                        type="button"
                        onClick={() => openQuickAdd()}
                    >
                        + New patient
                    </button>
                )}
            </div>
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

            {showQuickAdd && (
                <div className="quick-add-form">
                    <p className="quick-add-title">Create a new patient</p>
                    <div className="quick-add-grid">
                        <input
                            name="name"
                            placeholder="Name"
                            value={quickAddForm.name}
                            onChange={handleQuickAddChange}
                            onKeyDown={handleQuickAddKeyDown}
                        />
                        <input
                            name="phone"
                            placeholder="Phone"
                            value={quickAddForm.phone}
                            onChange={handleQuickAddChange}
                            onKeyDown={handleQuickAddKeyDown}
                        />
                        <input
                            name="email"
                            placeholder="Email (optional)"
                            value={quickAddForm.email}
                            onChange={handleQuickAddChange}
                            onKeyDown={handleQuickAddKeyDown}
                        />
                    </div>
                    {quickAddError && <p className="status-message error">{quickAddError}</p>}
                    <div className="quick-add-actions">
                        <button
                            className="btn"
                            type="button"
                            onClick={() => void handleQuickAddSubmit()}
                            disabled={creating}
                        >
                            {creating ? "Creating..." : "Create patient"}
                        </button>
                        <button className="btn secondary" type="button" onClick={closeQuickAdd}>
                            Cancel
                        </button>
                    </div>
                </div>
            )}

            {loading && <p className="status-message">Loading patients...</p>}
            {!showQuickAdd && showSelectionHint && <p className="patient-selector-helper">Select a patient from the list.</p>}
            {!showQuickAdd && error && <p className="status-message error">{error}</p>}

            {!showQuickAdd && !loading && !error && patients.length === 0 && (
                <div className="patient-selector-empty">
                    <p>No patients found yet.</p>
                    <button className="btn" type="button" onClick={() => openQuickAdd()}>
                        + Create patient
                    </button>
                </div>
            )}

            {!showQuickAdd && isOpen && !loading && !error && patients.length > 0 && (
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
                        <div className="patient-selector-option quickadd-option">
                            <span>No patient matches your search.</span>
                            <button
                                className="btn secondary"
                                type="button"
                                onClick={() => openQuickAdd(inputValue)}
                            >
                                + Add "{inputValue}" as a new patient
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default PatientSelector;