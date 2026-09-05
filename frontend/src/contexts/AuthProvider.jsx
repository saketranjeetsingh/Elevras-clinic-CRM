import { useCallback, useEffect, useState } from "react";
import { AuthContext } from "./AuthContext";
import api from "../services/api";

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [organizations, setOrganizations] = useState([]);

    const fetchMe = useCallback(async () => {
        const token = localStorage.getItem("token");

        if (!token) {
            setUser(null);
            setLoading(false);
            return;
        }

        try {
            const res = await api.get("/auth/me");
            const userData = res.data;
            setUser({
                id: userData.id,
                email: userData.email,
                name: userData.name,
                is_active: userData.is_active,
                organization_id: userData.organization_id,
                roles: userData.roles || [],
                permissions: userData.permissions || [],
            });
            if (userData.organizations) {
                setOrganizations(userData.organizations);
            }
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
            const data = res.data;
            setUser({
                id: data.id,
                email: data.email,
                name: data.name,
                is_active: data.is_active,
                organization_id: data.organization_id,
                roles: data.roles || [],
                permissions: data.permissions || [],
            });
            if (data.organizations) {
                setOrganizations(data.organizations);
            }
        } catch (err) {
            localStorage.removeItem("token");
            setUser(null);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    const logout = async () => {
        try {
            await api.post("/auth/logout");
        } catch {
            // Ignore logout errors
        }
        localStorage.removeItem("token");
        setUser(null);
        setOrganizations([]);
    };

    const switchOrganization = async (organizationId) => {
        const res = await api.post("/auth/switch-organization", { organization_id: organizationId });
        const data = res.data;
        setUser({
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            is_active: data.user.is_active,
            organization_id: data.user.organization_id,
            roles: data.user.roles || [],
            permissions: data.user.permissions || [],
        });
        return data;
    };

    const refreshToken = async () => {
        const res = await api.post("/auth/refresh");
        const data = res.data;
        setUser({
            id: data.user.id,
            email: data.user.email,
            name: data.user.name,
            is_active: data.user.is_active,
            organization_id: data.user.organization_id,
            roles: data.user.roles || [],
            permissions: data.user.permissions || [],
        });
        return data;
    };

    const hasPermission = (permission) => {
        if (!user) return false;
        return user.permissions?.includes(permission) || user.roles?.includes("admin");
    };

    const hasRole = (role) => {
        if (!user) return false;
        return user.roles?.includes(role);
    };

    const canAccess = (requiredPermissions) => {
        if (!user) return false;
        if (user.roles?.includes("admin")) return true;
        return requiredPermissions.some((p) => user.permissions?.includes(p));
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                organizations,
                login,
                logout,
                switchOrganization,
                refreshToken,
                hasPermission,
                hasRole,
                canAccess,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;