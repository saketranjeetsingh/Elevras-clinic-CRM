import { describe, it, expect, vi, beforeEach } from "vitest";
import { useContext } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const apiMock = vi.hoisted(() => ({ get: vi.fn() }));

vi.mock("../services/api", () => ({
    default: apiMock,
}));

import { AuthProvider } from "./AuthProvider";
import { AuthContext } from "./AuthContext";

function TestConsumer() {
    const { user, login, logout } = useContext(AuthContext);
    return (
        <div>
            <div data-testid="user">{user ? user.name : "none"}</div>
            <button onClick={() => login("token-abc").catch(() => {})}>login</button>
            <button onClick={logout}>logout</button>
        </div>
    );
}

describe("AuthContext", () => {
    beforeEach(() => {
        localStorage.clear();
        apiMock.get.mockReset();
    });

    it("logs in by storing the token and fetching the profile", async () => {
        apiMock.get.mockResolvedValue({ 
            data: { 
                id: 1,
                name: "Dr. Alice", 
                email: "alice@example.com",
                is_active: true,
                organization_id: 1,
                roles: ["admin"],
                permissions: ["patient:view"],
                organizations: [1],
                doctor_profile_id: 1
            } 
        });
        const user = userEvent.setup();

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await user.click(screen.getByText("login"));

        await waitFor(() => {
            expect(screen.getByTestId("user")).toHaveTextContent("Dr. Alice");
        });
        expect(localStorage.getItem("token")).toBe("token-abc");
        expect(localStorage.getItem("organization_id")).toBe("1");
        expect(apiMock.get).toHaveBeenCalledWith("/auth/me");
    });

    it("clears the token and user when login fails", async () => {
        apiMock.get.mockRejectedValue({ response: { data: { detail: "Invalid token" } } });
        const user = userEvent.setup();

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await user.click(screen.getByText("login"));

        await waitFor(() => {
            expect(screen.getByTestId("user")).toHaveTextContent("none");
        });
        expect(localStorage.getItem("token")).toBeNull();
        expect(localStorage.getItem("organization_id")).toBeNull();
    });

    it("restores the user from a stored token on mount", async () => {
        localStorage.setItem("token", "stored-token");
        localStorage.setItem("organization_id", "2");
        apiMock.get.mockResolvedValue({ 
            data: { 
                id: 2,
                name: "Dr. Bob", 
                email: "bob@example.com",
                is_active: true,
                organization_id: 2,
                roles: ["doctor"],
                permissions: ["patient:view"],
                organizations: [2],
                doctor_profile_id: 2
            } 
        });

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId("user")).toHaveTextContent("Dr. Bob");
        });
        expect(apiMock.get).toHaveBeenCalledWith("/auth/me");
    });

    it("logs out by clearing the token and user", async () => {
        localStorage.setItem("token", "token-abc");
        localStorage.setItem("organization_id", "1");
        apiMock.get.mockResolvedValue({ 
            data: { 
                id: 1,
                name: "Dr. Alice", 
                email: "alice@example.com",
                is_active: true,
                organization_id: 1,
                roles: ["admin"],
                permissions: ["patient:view"],
                organizations: [1],
                doctor_profile_id: 1
            } 
        });
        const user = userEvent.setup();

        render(
            <AuthProvider>
                <TestConsumer />
            </AuthProvider>
        );

        await waitFor(() => {
            expect(screen.getByTestId("user")).toHaveTextContent("Dr. Alice");
        });

        await user.click(screen.getByText("logout"));

        expect(screen.getByTestId("user")).toHaveTextContent("none");
        expect(localStorage.getItem("token")).toBeNull();
        expect(localStorage.getItem("organization_id")).toBeNull();
    });
});
