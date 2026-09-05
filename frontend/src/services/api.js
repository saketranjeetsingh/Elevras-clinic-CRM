import axios from "axios";

const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

const api = axios.create({
    baseURL: apiBaseUrl,
    withCredentials: true, // Important for refresh token cookie
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

function extractValidationDetail(data) {
    const detail = data?.detail ?? data?.message;

    if (Array.isArray(detail)) {
        const parts = detail
            .map((item) => {
                if (!item || typeof item !== "object") return null;
                const loc = Array.isArray(item.loc) ? item.loc.slice(1).join(".").replace(/_/g, " ") : "";
                const msg = typeof item.msg === "string" && item.msg.trim() ? item.msg.trim() : "";
                if (!msg) return null;
                const field = loc ? `${loc}: ` : "";
                return `${field}${msg.charAt(0).toUpperCase()}${msg.slice(1)}`;
            })
            .filter(Boolean);

        if (parts.length) return parts.join(", ");
    }

    if (typeof detail === "string" && detail.trim()) return detail.trim();

    return null;
}

function normalizeError(error) {
    if (!error) {
        return { detail: "Something went wrong. Please try again.", message: "Something went wrong. Please try again." };
    }

    if (error?.code === "ERR_NETWORK" || error?.message === "Network Error" || !error?.response) {
        return { detail: "Network unavailable.", message: "Network unavailable." };
    }

    const status = error.response?.status;
    const serverDetail = error.response?.data?.detail || error.response?.data?.message;
    const lowered = String(serverDetail || "").toLowerCase();

    if (status === 401 || status === 403 || lowered.includes("unauthorized") || lowered.includes("invalid credentials")) {
        return { detail: "Session expired. Please log in again.", message: "Session expired. Please log in again." };
    }

    if (status === 422 || lowered.includes("validation failed")) {
        const validationMessage = extractValidationDetail(error.response?.data);
        const detail = validationMessage || "Please check your details and try again.";
        return { detail, message: detail };
    }

    if (lowered.includes("patient already exists")) {
        return { detail: "Patient already exists.", message: "Patient already exists." };
    }

    if (lowered.includes("invalid email")) {
        return { detail: "We could not find that email.", message: "We could not find that email." };
    }

    if (lowered.includes("invalid password")) {
        return { detail: "Incorrect password.", message: "Incorrect password." };
    }

    if (lowered.includes("already exists") || lowered.includes("already registered")) {
        return { detail: "Email already exists.", message: "Email already exists." };
    }

    if (status >= 500) {
        return { detail: "Server unavailable.", message: "Server unavailable." };
    }

    return { detail: "Something went wrong. Please try again.", message: "Something went wrong. Please try again." };
}

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        const orgId = localStorage.getItem("organization_id");

        config.headers = {
            ...(config.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(orgId ? { "X-Organization-ID": orgId } : {}),
        };

        return config;
    }
);

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                }).catch((err) => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const res = await api.post("/auth/refresh");
                const newToken = res.data.access_token;
                localStorage.setItem("token", newToken);

                processQueue(null, newToken);
                originalRequest.headers.Authorization = `Bearer ${newToken}`;
                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);
                localStorage.removeItem("token");
                window.location.href = "/";
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(normalizeError(error))
    }
);

// Small wrappers for consistent error handling in pages
export async function get(path, params) {
    try {
        const res = await api.get(path, { params });
        return res.data;
    } catch (err) {
        throw err.response?.data || err;
    }
}

export async function post(path, data) {
    try {
        const res = await api.post(path, data);
        return res.data;
    } catch (err) {
        throw err.response?.data || err;
    }
}

export async function postForm(path, formData) {
    try {
        const res = await api.post(path, formData);
        return res.data;
    } catch (err) {
        throw err.response?.data || err;
    }
}

export async function put(path, data, params) {
    try {
        const res = await api.put(path, data, { params });
        return res.data;
    } catch (err) {
        throw err.response?.data || err;
    }
}

export async function del(path) {
    try {
        const res = await api.delete(path);
        return res.data;
    } catch (err) {
        throw err.response?.data || err;
    }
}

export default api;