import { useState } from "react";
import { post, postForm } from "../services/api";
import { useToast } from "../components/ToastContext";

function Import() {
    const [file, setFile] = useState(null);
    const [previewData, setPreviewData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [confirming, setConfirming] = useState(false);
    const toast = useToast();

    const handleFileSelect = (e) => {
        const selected = e.target.files[0];
        if (selected) {
            setFile(selected);
            setPreviewData(null);
        }
    };

    const handlePreview = async (e) => {
        e.preventDefault();
        if (!file) {
            toast.error("Please select a CSV file");
            return;
        }

        setLoading(true);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const data = await postForm("/patients/import/preview", formData);
            setPreviewData(data);

            if (data.total_rows === 0) {
                toast.error("CSV file is empty");
            } else if (data.invalid_rows > 0 || data.errors.length > 0) {
                toast.error(`Found ${data.invalid_rows} invalid rows. Please review the data.`);
            }
        } catch (err) {
            toast.error(err?.detail || err?.message || "Preview failed");
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async () => {
        if (!previewData || !previewData.preview_rows) {
            toast.error("No preview data to confirm");
            return;
        }

        setConfirming(true);

        try {
            const result = await post("/patients/import/confirm", {
                rows: previewData.preview_rows,
            });

            toast.success(
                `Import complete: ${result.imported_count} patients imported, ${result.skipped_duplicates} duplicates skipped.`
            );
            setPreviewData(null);
            setFile(null);
        } catch (err) {
            toast.error(err?.detail || err?.message || "Import failed");
        } finally {
            setConfirming(false);
        }
    };

    const handleCancel = () => {
        setFile(null);
        setPreviewData(null);
    };

    return (
        <div className="page">
            <div className="page-header page-header-card">
                <div>
                    <p className="eyebrow">
                        <span className="eyebrow-icon">
                            <svg
                                viewBox="0 0 24 24"
                                width="14"
                                height="14"
                                fill="currentColor"
                                aria-hidden="true"
                            >
                                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                            </svg>
                        </span>
                        Import Patients
                    </p>
                    <h1>Bulk import your patient roster</h1>
                    <p className="page-subtitle">
                        Upload a CSV file to quickly add multiple patients to your roster at once.
                    </p>
                </div>
            </div>

            <section className="section-card form-card">
                <div className="section-heading-row">
                    <h2>{previewData ? "Review Preview" : "Select CSV File"}</h2>
                    <span className="muted-chip">Import Data</span>
                </div>

                {!previewData ? (
                    <form onSubmit={handlePreview}>
                        <div className="form-field">
                            <label htmlFor="csv-file">
                                CSV File
                            </label>
                            <input
                                id="csv-file"
                                type="file"
                                accept=".csv"
                                onChange={handleFileSelect}
                                disabled={loading}
                                required
                            />
                            <p className="form-help">
                                Your CSV should include columns for: name, phone, email, age, gender, blood_group, medical_history, notes, and last_treatment.
                            </p>
                        </div>
                        <div className="action-row">
                            <button type="submit" className="btn" disabled={loading || !file}>
                                {loading ? "Previewing..." : "Preview"}
                            </button>
                        </div>
                    </form>
                ) : (
                    <div>
                        <div className="summary-grid">
                            <div className="summary-item">
                                <span className="summary-label">Total Rows</span>
                                <span className="summary-value">{previewData.total_rows}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Valid</span>
                                <span className="summary-value">{previewData.valid_rows}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Invalid</span>
                                <span className="summary-value">{previewData.invalid_rows}</span>
                            </div>
                            <div className="summary-item">
                                <span className="summary-label">Duplicates</span>
                                <span className="summary-value">{previewData.duplicates.length}</span>
                            </div>
                        </div>

                        {previewData.mapped_columns && Object.keys(previewData.mapped_columns).length > 0 && (
                            <div className="preview-section">
                                <h3>Mapped Columns</h3>
                                <div className="mapped-columns">
                                    {Object.entries(previewData.mapped_columns).map(([csvHeader, field]) => (
                                        <div key={field} className="mapped-column">
                                            <span className="csv-header">{csvHeader}</span>
                                            <span className="arrow">→</span>
                                            <span className="field-name">{field}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {previewData.unmapped_columns && previewData.unmapped_columns.length > 0 && (
                            <div className="preview-section">
                                <h3>Unmapped Columns</h3>
                                <p className="muted">These columns were not recognized and will be ignored:</p>
                                <ul>
                                    {previewData.unmapped_columns.map((col, i) => (
                                        <li key={i}>{col}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {previewData.errors && previewData.errors.length > 0 && (
                            <div className="preview-section error-section">
                                <h3>Invalid Rows</h3>
                                {previewData.errors.map((errItem, i) => (
                                    <div key={i} className="error-item">
                                        <strong>Row {errItem.row_number}:</strong> {errItem.errors.join(", ")}
                                    </div>
                                ))}
                            </div>
                        )}

                        {previewData.duplicates && previewData.duplicates.length > 0 && (
                            <div className="preview-section warning-section">
                                <h3>Duplicate Patients</h3>
                                <p className="muted">These rows match existing patients and will be skipped:</p>
                                {previewData.duplicates.map((dup, i) => (
                                    <div key={i} className="warning-item">
                                        Row {dup.row_number} — Duplicate phone or email (Patient ID: {dup.duplicate_id})
                                    </div>
                                ))}
                            </div>
                        )}

                        {previewData.preview_rows && previewData.preview_rows.length > 0 && (
                            <div className="preview-section">
                                <h3>Preview Data</h3>
                                <p className="muted">Showing first few rows to be imported:</p>
                                <div className="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Name</th>
                                                <th>Phone</th>
                                                <th>Email</th>
                                                <th>Age</th>
                                                <th>Gender</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {previewData.preview_rows.slice(0, 5).map((row, i) => (
                                                <tr key={i}>
                                                    <td>{row.name}</td>
                                                    <td>{row.phone}</td>
                                                    <td>{row.email}</td>
                                                    <td>{row.age || "-"}</td>
                                                    <td>{row.gender || "-"}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                {previewData.preview_rows.length > 5 && (
                                    <p className="muted">... and {previewData.preview_rows.length - 5} more rows</p>
                                )}
                            </div>
                        )}

                        <div className="action-row">
                            {previewData.valid_rows > 0 && previewData.invalid_rows === 0 && (
                                <button
                                    type="button"
                                    className="btn"
                                    onClick={handleConfirm}
                                    disabled={confirming}
                                >
                                    {confirming ? "Importing..." : "Confirm Import"}
                                </button>
                            )}
                            <button type="button" className="btn secondary" onClick={handleCancel}>
                                {previewData ? "Upload Different File" : "Cancel"}
                            </button>
                        </div>
                    </div>
                )}
            </section>

            <section className="section-card">
                <h2>CSV Format Guide</h2>
                <p>Your CSV file should have the following structure:</p>
                <div className="code-block">
                    <pre>
{`name,phone,email,age,gender,blood_group,medical_history,notes,last_treatment
John Doe,1234567890,john@example.com,30,Male,O+,None,Regular checkup,2024-01-15
Jane Smith,9876543210,jane@example.com,28,Female,A-,Diabetes,Follow up,2024-01-14`}
                    </pre>
                </div>
                <ul>
                    <li><strong>Required:</strong> name, phone</li>
                    <li><strong>Optional:</strong> email, age, gender, blood_group, medical_history, notes, last_treatment</li>
                    <li>Column headers are case-insensitive</li>
                    <li>Duplicate phone or email addresses will be automatically skipped</li>
                    <li>Invalid rows are reported but don't block the entire import</li>
                </ul>
            </section>
        </div>
    );
}

export default Import;