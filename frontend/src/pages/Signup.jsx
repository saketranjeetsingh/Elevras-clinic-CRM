import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

function Signup() {
    const navigate = useNavigate();
    const [form, setForm] = useState({
        name: "",
        email: "",
        password: "",
        clinic_name: "",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const validateForm = () => {
        if (!form.name.trim()) {
            setError("Please enter your doctor name.");
            return false;
        }

        if (!form.email.trim() || !form.email.includes("@")) {
            setError("Please enter a valid email address.");
            return false;
        }

        if (form.password.length < 6) {
            setError("Password must be at least 6 characters long.");
            return false;
        }

        if (!form.clinic_name.trim()) {
            setError("Please enter your clinic name.");
            return false;
        }

        return true;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setSuccess("");

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            await api.post("/auth/signup", {
                name: form.name.trim(),
                email: form.email.trim(),
                password: form.password,
                clinic_name: form.clinic_name.trim(),
            });
            setSuccess("Account created successfully. You can sign in now.");
            setTimeout(() => navigate("/"), 800);
        } catch (err) {
            setError(err?.detail || err?.message || "We could not create your account. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card">
                <div className="auth-brand">
                    <div className="brand-mark">EC</div>
                    <div>
                        <h2>Elevras Clinic</h2>
                        <p>Start your care dashboard</p>
                    </div>
                </div>

                <div className="auth-header">
                    <h1>Create account</h1>
                    <p>Set up your doctor and clinic profile to get started.</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <label className="field-label" htmlFor="doctorName">Doctor Name</label>
                    <input id="doctorName" name="name" placeholder="Doctor Name" value={form.name} onChange={handleChange} />
                    <label className="field-label" htmlFor="email">Email</label>
                    <input id="email" name="email" type="email" placeholder="Email address" value={form.email} onChange={handleChange} />

                    <div className="auth-input-group">
                        <input
                            name="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="Password"
                            value={form.password}
                            onChange={handleChange}
                        />
                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setShowPassword((value) => !value)}
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                    </div>

                    <label className="field-label" htmlFor="clinicName">Clinic Name</label>
                    <input id="clinicName" name="clinic_name" placeholder="Clinic Name" value={form.clinic_name} onChange={handleChange} />
                    <button className="btn auth-submit" type="submit" disabled={loading}>
                        {loading ? "Creating account..." : "Create account"}
                    </button>
                </form>

                {error && <p className="status-message error">{error}</p>}
                {success && <p className="status-message success">{success}</p>}
                <p className="auth-link-row">
                    Already have an account? <Link to="/" className="auth-link">Login</Link>
                </p>
            </div>
        </div>
    );
}

export default Signup;
