import { describe, it, expect, beforeEach, vi } from "vitest";

const mockInstance = vi.hoisted(() => ({
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
    },
}));

vi.mock("axios", () => ({
    default: {
        create: vi.fn(() => mockInstance),
    },
}));

import { get, post, postForm, put, del } from "./api";

const requestInterceptor = mockInstance.interceptors.request.use.mock.calls[0][0];
const responseErrorInterceptor = mockInstance.interceptors.response.use.mock.calls[0][1];

describe("api client", () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it("attaches the auth header when a token exists", () => {
        localStorage.setItem("token", "token-123");
        localStorage.setItem("organization_id", "1");
        const config = { headers: {} };
        requestInterceptor(config);
        expect(config.headers.Authorization).toBe("Bearer token-123");
        expect(config.headers["X-Organization-ID"]).toBe("1");
    });

    it("does not attach an auth header without a token", () => {
        const config = { headers: {} };
        requestInterceptor(config);
        expect(config.headers.Authorization).toBeUndefined();
        expect(config.headers["X-Organization-ID"]).toBeUndefined();
    });

    it("attaches X-Organization-ID when org_id exists but no token", () => {
        localStorage.setItem("organization_id", "2");
        const config = { headers: {} };
        requestInterceptor(config);
        expect(config.headers.Authorization).toBeUndefined();
        expect(config.headers["X-Organization-ID"]).toBe("2");
    });

    it("get() resolves with response data", async () => {
        mockInstance.get.mockResolvedValue({ data: [{ id: 1 }] });
        await expect(get("/patients")).resolves.toEqual([{ id: 1 }]);
        expect(mockInstance.get).toHaveBeenCalledWith("/patients", { params: undefined });
    });

    it("post() resolves with response data", async () => {
        mockInstance.post.mockResolvedValue({ data: { id: 2 } });
        await expect(post("/patients", { name: "Alice" })).resolves.toEqual({ id: 2 });
        expect(mockInstance.post).toHaveBeenCalledWith("/patients", { name: "Alice" });
    });

    it("postForm() forwards the form data", async () => {
        const formData = new FormData();
        formData.append("file", "csv");
        mockInstance.post.mockResolvedValue({ data: { valid_rows: 1 } });
        await expect(postForm("/patients/import/preview", formData)).resolves.toEqual({
            valid_rows: 1,
        });
        expect(mockInstance.post).toHaveBeenCalledWith("/patients/import/preview", formData);
    });

    it("put() resolves with response data", async () => {
        mockInstance.put.mockResolvedValue({ data: { id: 2, status: "Completed" } });
        await expect(put("/appointments/2", { status: "Completed" })).resolves.toEqual({
            id: 2,
            status: "Completed",
        });
    });

    it("del() resolves with response data", async () => {
        mockInstance.delete.mockResolvedValue({ data: { message: "Deleted" } });
        await expect(del("/patients/1")).resolves.toEqual({ message: "Deleted" });
    });

    it("normalizes a 401 error after refresh fails", async () => {
        // Mock refresh to fail
        mockInstance.post.mockImplementation((url) => {
            if (url === "/auth/refresh") {
                return Promise.reject({ response: { status: 401, data: { detail: "Invalid refresh token" } } });
            }
            return Promise.resolve({ data: {} });
        });

        const error = { 
            response: { status: 401, data: { detail: "Invalid credentials" } },
            config: { _retry: false, headers: {} }
        };
        await expect(responseErrorInterceptor(error)).rejects.toEqual({
            detail: "Session expired. Please log in again.",
            message: "Session expired. Please log in again.",
        });
    });

    it("normalizes a network error", async () => {
        await expect(responseErrorInterceptor({ code: "ERR_NETWORK" })).rejects.toEqual({
            detail: "Network unavailable.",
            message: "Network unavailable.",
        });
    });

    it("normalizes a 422 validation error into readable field messages", async () => {
        const error = {
            response: {
                status: 422,
                data: { detail: [{ loc: ["body", "phone"], msg: "field required" }] },
            },
            config: {}
        };
        await expect(responseErrorInterceptor(error)).rejects.toEqual({
            detail: "phone: Field required",
            message: "phone: Field required",
        });
    });
});
