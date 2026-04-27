import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";
import TaglineSection from "./TaglineSection";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

const STORAGE_KEY = "demo-auth-session";

const readStoredSession = () => {
  const savedSession = localStorage.getItem(STORAGE_KEY);
  if (!savedSession) {
    return null;
  }

  try {
    return JSON.parse(savedSession);
  } catch (error) {
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
};

const getAuthHeader = (token) => {
  if (!token) {
    return {};
  }

  return {
    Authorization: `Bearer ${token}`,
  };
};

function App() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({
    id: "",
    name: "",
    desc: "",
    price: "",
    quantity: "",
  });
  const [authMode, setAuthMode] = useState("login");
  const [authForm, setAuthForm] = useState({
    username: "",
    email: "",
    password: "",
    full_name: "",
    role: "viewer",
  });
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [authError, setAuthError] = useState("");
  const [loading, setLoading] = useState(false);
  const [authLoading, setAuthLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [sortField, setSortField] = useState("id");
  const [sortDirection, setSortDirection] = useState("asc");
  const [session, setSession] = useState(readStoredSession);

  useEffect(() => {
    if (message) {
      const timer = setTimeout(() => {
        setMessage("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [message]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        setError("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  useEffect(() => {
    if (authError) {
      const timer = setTimeout(() => {
        setAuthError("");
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [authError]);

  const authRequest = async (config, token = session?.access_token) => {
    return api({
      ...config,
      headers: {
        ...(config.headers || {}),
        ...getAuthHeader(token),
      },
    });
  };

  const fetchProducts = async (token = session?.access_token) => {
    if (!token) {
      return;
    }

    setLoading(true);
    try {
      const res = await authRequest(
        {
          method: "get",
          url: "/products/",
        },
        token
      );
      setProducts(res.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch products");
    }
    setLoading(false);
  };

  useEffect(() => {
    const bootstrapAuth = async () => {
      if (!session?.access_token) {
        setAuthLoading(false);
        return;
      }

      try {
        const res = await authRequest(
          {
            method: "get",
            url: "/auth/me",
          },
          session.access_token
        );
        const nextSession = {
          access_token: session.access_token,
          token_type: session.token_type || "bearer",
          user: res.data,
        };
        setSession(nextSession);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(nextSession));
        await fetchProducts(session.access_token);
      } catch (err) {
        localStorage.removeItem(STORAGE_KEY);
        setSession(null);
        setProducts([]);
        setAuthError("Your saved session has expired. Please sign in again.");
      }
      setAuthLoading(false);
    };

    bootstrapAuth();
  }, []);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const filteredProducts = useMemo(() => {
    let filtered = [...products];

    const q = filter.trim().toLowerCase();
    if (q) {
      filtered = filtered.filter((p) =>
        String(p.id).includes(q) ||
        p.name?.toLowerCase().includes(q) ||
        p.desc?.toLowerCase().includes(q)
      );
    }

    return filtered.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (sortField === "id" || sortField === "price" || sortField === "quantity") {
        aVal = Number(aVal);
        bVal = Number(bVal);
      } else {
        aVal = String(aVal).toLowerCase();
        bVal = String(bVal).toLowerCase();
      }

      if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
      if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
      return 0;
    });
  }, [products, filter, sortField, sortDirection]);

  const canWrite = session?.user?.permissions?.includes("write");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleAuthChange = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
  };

  const resetForm = () => {
    setForm({ id: "", name: "", desc: "", price: "", quantity: "" });
    setEditId(null);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    setMessage("");
    setError("");

    try {
      const res = await api.post("/auth/login", {
        username: authForm.username,
        password: authForm.password,
      });
      setSession(res.data);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(res.data));
      await fetchProducts(res.data.access_token);
    } catch (err) {
      setAuthError(err.response?.data?.detail || "Login failed");
    }
    setAuthLoading(false);
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    setMessage("");

    try {
      await api.post("/auth/register", {
        username: authForm.username,
        email: authForm.email,
        password: authForm.password,
        full_name: authForm.full_name,
        role: authForm.role,
      });
      setMessage("User created successfully. You can sign in now.");
      setAuthMode("login");
      setAuthForm({
        username: authForm.username,
        email: "",
        password: "",
        full_name: "",
        role: "viewer",
      });
    } catch (err) {
      setAuthError(err.response?.data?.detail || "Registration failed");
    }
    setAuthLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setSession(null);
    setProducts([]);
    setAuthForm({
      username: "",
      email: "",
      password: "",
      full_name: "",
      role: "viewer",
    });
    resetForm();
    setMessage("");
    setError("");
    setAuthError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canWrite) {
      setError("Your account can view products but cannot change them.");
      return;
    }

    setLoading(true);
    setMessage("");
    setError("");
    try {
      const payload = {
        ...form,
        id: Number(form.id),
        price: Number(form.price),
        quantity: Number(form.quantity),
      };

      if (editId) {
        await authRequest({
          method: "put",
          url: `/products/${editId}`,
          data: payload,
        });
        setMessage("Product updated successfully");
      } else {
        await authRequest({
          method: "post",
          url: "/products/",
          data: payload,
        });
        setMessage("Product created successfully");
      }
      resetForm();
      await fetchProducts();
    } catch (err) {
      setError(err.response?.data?.detail || "Operation failed");
    }
    setLoading(false);
  };

  const handleEdit = (product) => {
    if (!canWrite) {
      setError("Your account can view products but cannot edit them.");
      return;
    }

    setForm({
      id: product.id,
      name: product.name,
      desc: product.desc,
      price: product.price,
      quantity: product.quantity,
    });
    setEditId(product.id);
    setMessage("");
    setError("");
  };

  const handleDelete = async (id) => {
    if (!canWrite) {
      setError("Your account can view products but cannot delete them.");
      return;
    }

    const ok = window.confirm("Delete this product?");
    if (!ok) return;

    setLoading(true);
    setMessage("");
    setError("");
    try {
      await authRequest({
        method: "delete",
        url: `/products/${id}`,
      });
      setMessage("Product deleted successfully");
      await fetchProducts();
    } catch (err) {
      setError(err.response?.data?.detail || "Delete failed");
    }
    setLoading(false);
  };

  const currency = (n) =>
    typeof n === "number" ? n.toFixed(2) : Number(n || 0).toFixed(2);

  if (authLoading && !session) {
    return (
      <div className="app-bg auth-screen">
        <div className="card auth-card">
          <h2>Checking session...</h2>
        </div>
      </div>
    );
  }

  if (!session) {
    const isRegisterMode = authMode === "register";

    return (
      <div className="app-bg auth-screen">
        <div className="card auth-card">
          <div className="auth-header">
            <span className="brand-badge">📦</span>
            <div>
              <h1>{isRegisterMode ? "Create User" : "FastAPI Demo Login"}</h1>
              <p>
                {isRegisterMode
                  ? "Create a database-backed user instead of editing credentials in code."
                  : "Sign in with a bearer-token based session."}
              </p>
            </div>
          </div>

          <div className="auth-switch">
            <button
              className={`btn ${authMode === "login" ? "" : "btn-secondary"}`}
              type="button"
              onClick={() => setAuthMode("login")}
            >
              Login
            </button>
            <button
              className={`btn ${authMode === "register" ? "" : "btn-secondary"}`}
              type="button"
              onClick={() => setAuthMode("register")}
            >
              Register
            </button>
          </div>

          <form
            onSubmit={isRegisterMode ? handleRegister : handleLogin}
            className="auth-form"
          >
            {isRegisterMode && (
              <input
                type="text"
                name="full_name"
                placeholder="Full name"
                value={authForm.full_name}
                onChange={handleAuthChange}
                required
              />
            )}
            <input
              type="text"
              name="username"
              placeholder="Username"
              value={authForm.username}
              onChange={handleAuthChange}
              required
            />
            {isRegisterMode && (
              <input
                type="email"
                name="email"
                placeholder="Email"
                value={authForm.email}
                onChange={handleAuthChange}
                required
              />
            )}
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={authForm.password}
              onChange={handleAuthChange}
              required
            />
            {isRegisterMode && (
              <select name="role" value={authForm.role} onChange={handleAuthChange}>
                <option value="viewer">viewer</option>
                <option value="editor">editor</option>
                <option value="admin">admin</option>
              </select>
            )}
            <button className="btn" type="submit" disabled={authLoading}>
              {authLoading
                ? isRegisterMode
                  ? "Creating..."
                  : "Signing in..."
                : isRegisterMode
                  ? "Create User"
                  : "Sign In"}
            </button>
          </form>

          <p className="muted auth-note">
            Registration succeeds only when the full name, email, and selected role match an
            approved combination. Accounts are then stored in PostgreSQL with hashed passwords.
          </p>

          {message && <div className="success-msg">{message}</div>}
          {authError && <div className="error-msg">{authError}</div>}
        </div>
      </div>
    );
  }

  return (
    <div className="app-bg">
      <header className="topbar">
        <div className="brand">
          <span className="brand-badge">📦</span>
          <div>
            <h1>Alok's Demo Website</h1>
            <p className="topbar-subtitle">
              Signed in as {session.user.full_name} ({session.user.role})
            </p>
          </div>
        </div>
        <div className="top-actions">
          <div className="user-pill">
            <span>{session.user.username}</span>
            <span className="muted">{canWrite ? "Write access" : "Read only"}</span>
          </div>
          <button className="btn btn-light" onClick={() => fetchProducts()} disabled={loading}>
            Refresh
          </button>
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      <div className="container">
        <div className="stats">
          <div className="chip">Total: {products.length}</div>
          <div className="chip">
            Access: {canWrite ? "Create / Update / Delete" : "Read only"}
          </div>
          <div className="search">
            <input
              type="text"
              placeholder="Search by id, name or desc..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>

        <div className="content-grid">
          <div className="card form-card">
            <h2>{editId ? "Edit Product" : "Add Product"}</h2>
            <form onSubmit={handleSubmit} className="product-form">
              <input
                type="number"
                name="id"
                placeholder="ID"
                value={form.id}
                onChange={handleChange}
                required
                disabled={!!editId || !canWrite}
              />
              <input
                type="text"
                name="name"
                placeholder="Name"
                value={form.name}
                onChange={handleChange}
                required
                disabled={!canWrite}
              />
              <input
                type="text"
                name="desc"
                placeholder="Description"
                value={form.desc}
                onChange={handleChange}
                required
                disabled={!canWrite}
              />
              <input
                type="number"
                name="price"
                placeholder="Price"
                value={form.price}
                onChange={handleChange}
                required
                step="0.01"
                disabled={!canWrite}
              />
              <input
                type="number"
                name="quantity"
                placeholder="Quantity"
                value={form.quantity}
                onChange={handleChange}
                required
                disabled={!canWrite}
              />
              <div className="form-actions">
                <button className="btn" type="submit" disabled={loading || !canWrite}>
                  {editId ? "Update" : "Add"}
                </button>
                {editId && (
                  <button
                    className="btn btn-secondary"
                    type="button"
                    onClick={() => {
                      resetForm();
                      setMessage("");
                      setError("");
                    }}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>
            {!canWrite && (
              <p className="muted access-note">
                This account is view-only. Use an `admin` or `editor` role to modify products.
              </p>
            )}
            {message && <div className="success-msg">{message}</div>}
            {error && <div className="error-msg">{error}</div>}
          </div>

          <TaglineSection />

          <div className="card list-card">
            <h2>Products</h2>
            {loading ? (
              <div className="loader">Loading...</div>
            ) : (
              <div className="scroll-x">
                <table className="product-table">
                  <thead>
                    <tr>
                      <th
                        className={`sortable ${sortField === "id" ? `sort-${sortDirection}` : ""}`}
                        onClick={() => handleSort("id")}
                      >
                        ID
                      </th>
                      <th
                        className={`sortable ${sortField === "name" ? `sort-${sortDirection}` : ""}`}
                        onClick={() => handleSort("name")}
                      >
                        Name
                      </th>
                      <th>Description</th>
                      <th
                        className={`sortable ${sortField === "price" ? `sort-${sortDirection}` : ""}`}
                        onClick={() => handleSort("price")}
                      >
                        Price
                      </th>
                      <th
                        className={`sortable ${sortField === "quantity" ? `sort-${sortDirection}` : ""}`}
                        onClick={() => handleSort("quantity")}
                      >
                        Quantity
                      </th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map((p) => (
                      <tr key={p.id}>
                        <td>{p.id}</td>
                        <td className="name-cell">{p.name}</td>
                        <td className="desc-cell" title={p.desc}>
                          {p.desc}
                        </td>
                        <td className="price-cell">${currency(p.price)}</td>
                        <td>
                          <span className="qty-badge">{p.quantity}</span>
                        </td>
                        <td>
                          <div className="row-actions">
                            <button
                              className="btn btn-edit"
                              onClick={() => handleEdit(p)}
                              disabled={!canWrite}
                            >
                              Edit
                            </button>
                            <button
                              className="btn btn-delete"
                              onClick={() => handleDelete(p.id)}
                              disabled={!canWrite}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredProducts.length === 0 && (
                      <tr>
                        <td colSpan={6} className="empty">
                          No products found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
