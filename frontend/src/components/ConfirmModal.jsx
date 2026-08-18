function ConfirmModal({ open, title = "Are you sure?", message, confirmLabel = "Confirm", onConfirm, onCancel }) {
    if (!open) {
        return null;
    }

    return (
        <div className="modal-backdrop" onClick={onCancel}>
            <div
                className="modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="confirm-modal-title"
                onClick={(event) => event.stopPropagation()}
            >
                <h3 id="confirm-modal-title">{title}</h3>
                <p>{message}</p>
                <div className="modal-actions">
                    <button className="btn secondary" type="button" onClick={onCancel}>
                        Cancel
                    </button>
                    <button className="btn danger" type="button" onClick={onConfirm}>
                        {confirmLabel}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ConfirmModal;
