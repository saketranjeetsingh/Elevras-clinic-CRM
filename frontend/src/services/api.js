import axios from "axios";

const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

const api = axios.create({
    baseURL: apiBaseUrl,
});

function normalizeError(error) {
    if (!error) {
        return { detail: "Something went wrong. Please try again.", message: "Something went wrong. Please try again." };
    }

    if (error?.code === "ERR_NETWORK" || error?.message === "Network Error" || !error?.response) {
        return { detail: "Network unavailable.", message: "Network unavailable." };
    }

    const status = error.response?.status;
    const serverDetail = error.response?.data?.detail || error.response?.data?.message;

    if (status === 401 || status === 403) {
        return { detail: "Unauthorized.", message: "Unauthorized." };
    }

    if (status === 422) {
        return { detail: "Validation failed.", message: "Validation failed." };
    }

    if (typeof serverDetail === "string") {
        const lowered = serverDetail.toLowerCase();

        if (lowered.includes("already exists") || lowered.includes("already registered")) {
            return { detail: serverDetail, message: serverDetail };
        }

        if (lowered.includes("invalid email")) {
            return { detail: "Invalid email.", message: "Invalid email." };
        }

        if (lowered.includes("invalid password")) {
            return { detail: "Invalid password.", message: "Invalid password." };
        }

        if (lowered.includes("invalid credentials")) {
            return { detail: "Unauthorized.", message: "Unauthorized." };
        }

        if (lowered.includes("validation failed")) {
            return { detail: "Validation failed.", message: "Validation failed." };
        }

        if (lowered.includes("patient already exists")) {
            return { detail: "Patient already exists.", message: "Patient already exists." };
        }
    }

    if (status >= 500) {
        return { detail: "Backend unavailable.", message: "Backend unavailable." };
    }

    return { detail: "Something went wrong. Please try again.", message: "Something went wrong. Please try again." };
}

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

        config.headers = {
            ...(config.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        };

        return config;
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => Promise.reject(normalizeError(error))
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