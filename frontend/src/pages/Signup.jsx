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

    const handleChange = (e) => {
        const { name, value } = e.target;
        setForm((s) => ({ ...s, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setSuccess("");

        try {
            await api.post("/auth/signup", form);
            setSuccess("Account created successfully. You can sign in now.");
            setTimeout(() => navigate("/"), 800);
        } catch (err) {
            setError(err?.detail || err?.message || "Signup failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page">
            <h1>Create Account</h1>

            <form onSubmit={handleSubmit} className="form-row" style={{ flexDirection: "column", alignItems: "flex-start" }}>
                <input name="name" placeholder="Full name" value={form.name} onChange={handleChange} required />
                <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required />
                <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} required />
                <input name="clinic_name" placeholder="Clinic name" value={form.clinic_name} onChange={handleChange} required />
                <button className="btn" type="submit" disabled={loading}>
                    {loading ? "Creating account..." : "Sign up"}
                </button>
            </form>

            {error && <p className="error">{error}</p>}
            {success && <p className="success">{success}</p>}
            <p style={{ marginTop: 12 }}>
                Already have an account? <Link to="/">Login</Link>
            </p>
        </div>
    );
}

export default Signup;
