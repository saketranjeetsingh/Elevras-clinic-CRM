import { describe, it, expect } from "vitest";
import { createPatientLookup, getPatientDisplay } from "./patientHelpers";

describe("createPatientLookup", () => {
    it("builds a Map keyed by patient id", () => {
        const patients = [
            { id: 1, name: "Alice" },
            { id: 2, name: "Bob" },
        ];
        const lookup = createPatientLookup(patients);
        expect(lookup.get(1)).toEqual({ id: 1, name: "Alice" });
        expect(lookup.get(2)).toEqual({ id: 2, name: "Bob" });
    });

    it("handles empty and undefined input", () => {
        expect(createPatientLookup().size).toBe(0);
        expect(createPatientLookup([]).size).toBe(0);
        expect(createPatientLookup(null).size).toBe(0);
    });
});

describe("getPatientDisplay", () => {
    it("returns patient name and phone", () => {
        expect(getPatientDisplay({ name: "Alice", phone: "123" })).toEqual({
            name: "Alice",
            phone: "123",
        });
    });

    it("falls back gracefully for missing patient data", () => {
        expect(getPatientDisplay(null)).toEqual({ name: "Unknown patient", phone: "" });
        expect(getPatientDisplay(undefined)).toEqual({ name: "Unknown patient", phone: "" });
        expect(getPatientDisplay({})).toEqual({ name: "Unknown patient", phone: "" });
    });
});
