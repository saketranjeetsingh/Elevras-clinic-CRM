import React, { createContext, useEffect, useState } from "react";
import api from "../services/api";

export const AuthContext = createContext({
    user: null,
    loading: true,
    login: async () => {},
    logout: () => {}
});

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchMe = async () => {
        const token = localStorage.getItem("token");

        if (!token) {
            setUser(null);
            setLoading(false);
            return;
        }

        try {
            const res = await api.get("/auth/me");
            setUser(res.data);
        } catch (err) {
            localStorage.removeItem("token");
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchMe();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const login = async (token) => {
        localStorage.setItem("token", token);
        setLoading(true);
        try {
            const res = await api.get("/auth/me");
            setUser(res.data);
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
