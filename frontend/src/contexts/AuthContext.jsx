import { createContext, useCallback, useEffect, useState } from "react";
import api from "../services/api";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext({
    user: null,
    loading: true,
    login: async () => {},
    logout: () => {}
});

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const normalizeUser = (profile) => ({
        ...profile,
        doctor_name: profile?.doctor_name || profile?.name || "",
        clinic_name: profile?.clinic_name || "",
    });

    const fetchMe = useCallback(async () => {
        const token = localStorage.getItem("token");

        if (!token) {
            setUser(null);
            setLoading(false);
            return;
        }

        try {
            const res = await api.get("/auth/me");
            setUser(normalizeUser(res.data));
        } catch {
            localStorage.removeItem("token");
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            void fetchMe();
        }, 0);

        return () => window.clearTimeout(timer);
    }, [fetchMe]);

    const login = async (token) => {
        localStorage.setItem("token", token);
        setLoading(true);
        try {
            const res = await api.get("/auth/me");
            setUser(normalizeUser(res.data));
        } catch (err) {
            localStorage.removeItem("token");
            setUser(null);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        setUser(null);
    };

    return (
        <AuthContext.Provider
            value={{ user, setUser, loading, login, logout }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export default AuthContext;
