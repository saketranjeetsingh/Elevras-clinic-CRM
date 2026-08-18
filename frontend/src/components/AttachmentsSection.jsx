import { useCallback, useEffect, useState } from "react";
import api, { del, get, postForm } from "../services/api";
import { useToast } from "./ToastContext";
import ConfirmModal from "./ConfirmModal";

function formatFileSize(bytes) {
    if (!bytes && bytes !== 0) {
        return "";
    }
    const value = Number(bytes);
    if (value < 1024) {
        return `${value} B`;
    }
    if (value < 1024 * 1024) {
        return `${(value / 1024).toFixed(0)} KB`;
    }
    return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}

function categoryLabel(category) {
    const labels = {
        "x-ray": "X-Ray",
        "prescription": "Prescription",
        "lab-report": "Lab report",
        "photo": "Photo",
        "other": "Other",
    };
    return labels[category] || "Other";
}

function AttachmentsSection({ patientId }) {
    const [attachments, setAttachments] = useState([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [file, setFile] = useState(null);
    const [category, setCategory] = useState("other");
    const [urlMap, setUrlMap] = useState({});
    const [pendingDeleteId, setPendingDeleteId] = useState(null);
    const toast = useToast();

    const fetchAttachments = useCallback(async () => {
        setLoading(true);
        try {
            const data = await get(`/patients/${patientId}/attachments`);
            setAttachments(data || []);
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not load attachments.");
        } finally {
            setLoading(false);
        }
    }, [patientId, toast]);

    useEffect(() => {
        if (patientId) {
            const timer = window.setTimeout(() => {
                void fetchAttachments();
            }, 0);

            return () => window.clearTimeout(timer);
        }
    }, [fetchAttachments, patientId]);

    const loadBlobUrl = async (attachment) => {
        if (urlMap[attachment.id]) {
            return urlMap[attachment.id];
        }

        try {
            const res = await api.get(`/attachments/${attachment.id}/file`, { responseType: "blob" });
            const objectUrl = URL.createObjectURL(res.data);
            setUrlMap((current) => ({ ...current, [attachment.id]: objectUrl }));
            return objectUrl;
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not load this file.");
            return null;
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!file) {
            toast.error("Please choose a file to upload.");
            return;
        }

        setUploading(true);
        try {
            const formData = new FormData();
            formData.append("file", file);
            formData.append("category", category);

            await postForm(`/patients/${patientId}/attachments`, formData);
            toast.success("File uploaded successfully");
            setFile(null);
            setCategory("other");
            await fetchAttachments();
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not upload the file.");
        } finally {
            setUploading(false);
        }
    };

    const handleView = async (attachment) => {
        const objectUrl = await loadBlobUrl(attachment);
        if (objectUrl) {
            window.open(objectUrl, "_blank", "noopener");
        }
    };

    const handleDeleteConfirm = async () => {
        if (!pendingDeleteId) {
            return;
        }

        const deleteId = pendingDeleteId;
        setPendingDeleteId(null);

        try {
            await del(`/patients/${patientId}/attachments/${deleteId}`);
            toast.success("File deleted successfully");
            setUrlMap((current) => {
                const next = { ...current };
                if (next[deleteId]) {
                    URL.revokeObjectURL(next[deleteId]);
                    delete next[deleteId];
                }
                return next;
            });
            await fetchAttachments();
        } catch (err) {
            toast.error(err?.detail || err?.message || "We could not delete the file.");
        }
    };

    const isImage = (attachment) => String(attachment.content_type || "").startsWith("image/");

    return (
        <section className="card profile-card">
            <div className="section-heading-row">
                <h2>Attachments</h2>
                <span className="muted-chip">{attachments.length} files</span>
            </div>

            <form onSubmit={handleUpload} className="attachment-upload-row">
                <div className="form-field">
                    <label htmlFor="attachment-category">Category</label>
                    <select
                        id="attachment-category"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                    >
                        <option value="x-ray">X-Ray</option>
                        <option value="prescription">Prescription</option>
                        <option value="lab-report">Lab report</option>
                        <option value="photo">Photo</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div className="form-field">
                    <label htmlFor="attachment-file">File</label>
                    <input
                        id="attachment-file"
                        type="file"
                        accept="image/jpeg,image/png,image/gif,image/webp,application/pdf"
                        onChange={(e) => setFile(e.target.files[0] || null)}
                        disabled={uploading}
                    />
                </div>
                <button className="btn" type="submit" disabled={uploading || !file}>
                    {uploading ? "Uploading..." : "Upload"}
                </button>
            </form>
            <p className="form-help">Images and PDFs up to 20 MB.</p>

            {loading ? (
                <div className="table-skeleton">
                    {Array.from({ length: 2 }).map((_, index) => (
                        <div className="skeleton-row" key={index} />
                    ))}
                </div>
            ) : attachments.length > 0 ? (
                <div className="attachments-grid">
                    {attachments.map((attachment) => (
                        <div key={attachment.id} className="attachment-item">
                            <div className="attachment-thumb">
                                {isImage(attachment) ? (
                                    <img
                                        src={urlMap[attachment.id]}
                                        alt={attachment.filename}
                                        onClick={() => void handleView(attachment)}
                                        style={{ cursor: "pointer" }}
                                    />
                                ) : (
                                    <div className="attachment-fallback">
                                        <span role="img" aria-hidden="true">📄</span>
                                        <span>PDF</span>
                                    </div>
                                )}
                            </div>
                            <div className="attachment-meta">
                                <span className="attachment-name" title={attachment.filename}>
                                    {attachment.filename}
                                </span>
                                <span className="attachment-sub">
                                    {categoryLabel(attachment.category)} • {formatFileSize(attachment.size)}
                                </span>
                                <div className="attachment-actions">
                                    <button className="attachment-view" type="button" onClick={() => void handleView(attachment)}>
                                        View
                                    </button>
                                    <button
                                        className="attachment-delete"
                                        type="button"
                                        onClick={() => setPendingDeleteId(attachment.id)}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="empty-state compact-empty">
                    <p>No attachments yet. Upload x-rays, reports, or photos for this patient.</p>
                </div>
            )}

            <ConfirmModal
                open={Boolean(pendingDeleteId)}
                title="Delete this file?"
                message="This will permanently remove the file. This action cannot be undone."
                confirmLabel="Delete"
                onConfirm={() => void handleDeleteConfirm()}
                onCancel={() => setPendingDeleteId(null)}
            />
        </section>
    );
}

export default AttachmentsSection;