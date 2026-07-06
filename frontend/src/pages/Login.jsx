import { useState, useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import { AuthContext } from "../contexts/AuthContext";

function Login() {
    const navigate = useNavigate();
    const { login } = useContext(AuthContext);

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    const validateForm = () => {
        if (!email.trim()) {
            setError("Please enter your email address.");
            return false;
        }

        if (!email.includes("@")) {
            setError("Please enter a valid email address.");
            return false;
        }

        if (!password) {
            setError("Please enter your password.");
            return false;
        }

        return true;
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            const response = await api.post(
                "/auth/login",
                new URLSearchParams({ username: email.trim(), password }),
                {
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                }
            );

            const token = response.data.access_token;

            await login(token);

            navigate("/dashboard");
        } catch (err) {
            setError(err?.detail || err?.message || "We could not sign you in. Please try again.");
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
                        <p>Care management made simple</p>
                    </div>
                </div>

                <div className="auth-header">
                    <h1>Welcome back</h1>
                    <p>Sign in to your clinic dashboard.</p>
                </div>

                <form onSubmit={handleLogin} className="auth-form">
                    <input
                        type="email"
                        placeholder="Email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <div className="auth-input-group">
                        <input
                            type={showPassword ? "text" : "password"}
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                        <button
                            type="button"
                            className="password-toggle"
                            onClick={() => setShowPassword((value) => !value)}
                        >
                            {showPassword ? "Hide" : "Show"}
                        </button>
                    </div>

                    <button className="btn auth-submit" type="submit" disabled={loading}>
                        {loading ? "Signing in..." : "Login"}
                    </button>
                </form>

                {error && <p className="status-message error">{error}</p>}
                <p className="auth-link-row">
                    Need an account? <Link to="/signup" className="auth-link">Create one</Link>
                </p>
            </div>
        </div>
    );
}

export default Login;