import { describe, it, expect, vi, beforeEach } from "vitest";
import { useContext } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const apiMock = vi.hoisted(() => ({ get: vi.fn() }));

vi.mock("../services/api", () => ({
    default: apiMock,
}));

import { AuthProvider, AuthContext } from "./AuthContext";

function TestConsumer() {
    const { user, login, logout } = useContext(AuthContext);
    return (
        <div>
            <div data-testid="user">{user ? user.doctor_name : "none"}</div>
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
        apiMock.get.mockResolvedValue({ data: { doctor_name: "Dr. Alice", clinic_name: "Clinic A" } });
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
    });

    it("restores the user from a stored token on mount", async () => {
        localStorage.setItem("token", "stored-token");
        apiMock.get.mockResolvedValue({ data: { name: "Dr. Bob", clinic_name: "Clinic B" } });

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
        apiMock.get.mockResolvedValue({ data: { doctor_name: "Dr. Alice" } });
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
    });
});
