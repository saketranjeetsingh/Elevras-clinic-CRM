import { useEffect, useState, useRef } from "react";
import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { get, post, put, del } from "../services/api";
import AuthContext from "../contexts/AuthContext";
import ConfirmModal from "../components/ConfirmModal";
import Icon from "../components/Icon";

export default function SettingsPage() {
    const { user, hasPermission } = useContext(AuthContext);

    const [users, setUsers] = useState([]);
    const [roles, setRoles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [formData, setFormData] = useState({
        email: "",
        name: "",
        role_code: "receptionist",
        password: "",
        is_active: true,
    });
    const [submitting, setSubmitting] = useState(false);

    const loadData = async () => {
        try {
            setLoading(true);
            const [usersRes, rolesRes] = await Promise.all([
                get("/users"),
                get("/roles"),
            ]);
            setUsers(usersRes);
            setRoles(rolesRes);
        } catch (err) {
            setError(err.detail || "Failed to load data");
        } finally {
            setLoading(false);
        }
    };

    const mountedRef = useRef(false);
    useEffect(() => {
        if (!mountedRef.current) {
            mountedRef.current = true;
            loadData();
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (submitting) return;

        setSubmitting(true);
        try {
            if (editingUser) {
                await put(`/users/${editingUser.id}`, {
                    email: formData.email,
                    name: formData.name,
                    is_active: formData.is_active,
                });
            } else {
                await post("/users", {
                    email: formData.email,
                    name: formData.name,
                    role_code: formData.role_code,
                    password: formData.password,
                });
            }
            setShowModal(false);
            await loadData();
        } catch (err) {
            setError(err.detail || "Failed to save user");
        } finally {
            setSubmitting(false);
        }
    };

    const handleEdit = (user) => {
        setEditingUser(user);
        setFormData({
            email: user.email,
            name: user.name,
            role_code: user.roles?.[0] || "receptionist",
            password: "",
            is_active: user.is_active,
        });
        setShowModal(true);
    };

    const handleNewUser = () => {
        setEditingUser(null);
        setFormData({
            email: "",
            name: "",
            role_code: "receptionist",
            password: "",
            is_active: true,
        });
        setShowModal(true);
    };

    const handleDeactivate = async (userId) => {
        if (!window.confirm("Are you sure you want to deactivate this user?")) return;
        try {
            await post(`/users/${userId}/deactivate`);
            await loadData();
        } catch (err) {
            setError(err.detail || "Failed to deactivate user");
        }
    };

    const handleActivate = async (userId) => {
        try {
            await post(`/users/${userId}/activate`);
            await loadData();
        } catch (err) {
            setError(err.detail || "Failed to activate user");
        }
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingUser(null);
        setFormData({
            email: "",
            name: "",
            role_code: "receptionist",
            password: "",
            is_active: true,
        });
    };

    const hasAccess = user && hasPermission("user:manage");

    if (!hasAccess) {
        return <Navigate to="/dashboard" replace />;
    }

    if (loading) {
        return (
            <div className="page">
                <div className="skeleton-card" />
            </div>
        );
    }

    return (
        <div className="page">
            <div className="page-header">
                <h1>Team & Settings</h1>
                <button className="btn btn-primary" onClick={handleNewUser}>
                    <Icon name="plus" size={16} /> Invite User
                </button>
            </div>

            {error && (
                <div className="status-card status-card-error" style={{ marginBottom: 16 }}>
                    <Icon name="alert" size={18} />
                    <span>{error}</span>
                    <button className="toast-close" onClick={() => setError(null)}>×</button>
                </div>
            )}

            <div className="card">
                <div className="card-header">
                    <h2>Organization Users</h2>
                </div>
                <div className="table-responsive">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((u) => (
                                <tr key={u.id}>
                                    <td>{u.name}</td>
                                    <td>{u.email}</td>
                                    <td>
                                        <span className={`badge badge-${u.roles?.includes("admin") ? "primary" : u.roles?.includes("doctor") ? "success" : "secondary"}`}>
                                            {u.roles?.join(", ") || "—"}
                                        </span>
                                    </td>
                                    <td>
                                        <span className={`status-badge ${u.is_active ? "status-active" : "status-inactive"}`}>
                                            {u.is_active ? "Active" : "Inactive"}
                                        </span>
                                    </td>
                                    <td>
                                        <div className="action-buttons">
                                            <button className="btn btn-sm btn-secondary" onClick={() => handleEdit(u)}>Edit</button>
                                            {u.is_active && u.id !== user.id ? (
                                                <button className="btn btn-sm btn-danger" onClick={() => handleDeactivate(u.id)}>Deactivate</button>
                                            ) : !u.is_active && u.id !== user.id ? (
                                                <button className="btn btn-sm btn-success" onClick={() => handleActivate(u.id)}>Activate</button>
                                            ) : null}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <ConfirmModal
                open={showModal}
                onClose={handleCloseModal}
                title={editingUser ? "Edit User" : "Invite New User"}
                confirmLabel={editingUser ? "Save" : "Invite"}
                cancelLabel="Cancel"
                onConfirm={handleSubmit}
            >
                <form>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                            disabled={editingUser}
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="name">Name</label>
                        <input
                            type="text"
                            id="name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>
                    {!editingUser && (
                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                type="password"
                                id="password"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                required
                                minLength={6}
                            />
                        </div>
                    )}
                    <div className="form-group">
                        <label htmlFor="role_code">Role</label>
                        <select
                            id="role_code"
                            value={formData.role_code}
                            onChange={(e) => setFormData({ ...formData, role_code: e.target.value })}
                        >
                            <option value="receptionist">Receptionist</option>
                            <option value="doctor">Doctor</option>
                            <option value="admin">Admin</option>
                            {roles.filter(r => r.organization_id).map((r) => (
                                <option key={r.id} value={r.code}>{r.name} (Custom)</option>
                            ))}
                        </select>
                    </div>
                    {editingUser && (
                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={formData.is_active}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                />
                                Active
                            </label>
                        </div>
                    )}
                </form>
            </ConfirmModal>
        </div>
    );
}