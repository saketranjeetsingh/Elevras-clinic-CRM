/* eslint-disable react-refresh/only-export-components */
import { createContext } from "react";

export const AuthContext = createContext({
    user: null,
    loading: true,
    organizations: [],
    login: async () => {},
    logout: () => {},
    switchOrganization: async () => {},
    refreshToken: async () => {},
    hasPermission: () => false,
    hasRole: () => false,
    canAccess: () => false,
});

export default AuthContext;