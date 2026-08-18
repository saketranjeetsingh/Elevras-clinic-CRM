import { useCallback, useMemo, useState } from "react";
import { ToastContext } from "./ToastContext";

let toastSequence = 0;

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);

    const removeToast = useCallback((id) => {
        setToasts((current) => current.filter((toast) => toast.id !== id));
    }, []);

    const pushToast = useCallback((type, message) => {
        const id = `toast-${++toastSequence}`;
        setToasts((current) => [...current, { id, type, message }]);
        window.setTimeout(() => removeToast(id), 4000);
        return id;
    }, [removeToast]);

    const value = useMemo(
        () => ({
            success: (message) => pushToast("success", message),
            error: (message) => pushToast("error", message),
            info: (message) => pushToast("info", message),
        }),
        [pushToast]
    );

    return (
        <ToastContext.Provider value={value}>
            {children}
            <div className="toast-region" role="region" aria-live="polite">
                {toasts.map((toastItem) => (
                    <div key={toastItem.id} className={`toast toast-${toastItem.type}`}>
                        <span>{toastItem.message}</span>
                        <button
                            type="button"
                            className="toast-close"
                            aria-label="Dismiss notification"
                            onClick={() => removeToast(toastItem.id)}
                        >
                            ×
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}