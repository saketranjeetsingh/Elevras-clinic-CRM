import { useCallback, useEffect, useMemo, useState } from "react";
import { ThemeContext } from "./ThemeContext";

const STORAGE_KEY = "theme";

function getInitialTheme() {
    try {
        return localStorage.getItem(STORAGE_KEY) === "dark" ? "dark" : "light";
    } catch {
        return "light";
    }
}

export function ThemeProvider({ children }) {
    const [theme, setTheme] = useState(getInitialTheme);

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch {
            return;
        }
    }, [theme]);

    const toggleTheme = useCallback(() => {
        setTheme((current) => (current === "light" ? "dark" : "light"));
    }, []);

    const value = useMemo(() => ({ theme, toggleTheme }), [theme, toggleTheme]);

    return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}