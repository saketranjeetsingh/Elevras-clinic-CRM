export function createPatientLookup(patients = []) {
    return new Map((patients || []).map((patient) => [patient.id, patient]));
}

export function getPatientDisplay(patient) {
    if (!patient) {
        return {
            name: "Unknown patient",
            phone: "",
        };
    }

    return {
        name: patient.name || "Unknown patient",
        phone: patient.phone || "",
    };
}
