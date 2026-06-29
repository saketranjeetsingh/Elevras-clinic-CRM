import axios from "axios";

const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const api = axios.create({
    baseURL: apiBaseUrl,
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");

        config.headers = config.headers || {};

        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        return config;
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