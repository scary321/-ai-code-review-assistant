import useDocumentTitle from "../hooks/useDocumentTitle.js";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useDocumentTitle("Create account");

  async function handleSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await register(name, email, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="font-mono text-signal text-2xl mb-1">&gt;_</div>
          <h1 className="font-mono text-xl font-semibold">codestand</h1>
          <p className="text-ink-muted text-sm mt-1">Create an account</p>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="label-eyebrow block mb-1.5">Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input-field"
              placeholder="Ada Lovelace"
            />
          </div>
          <div>
            <label className="label-eyebrow block mb-1.5">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="input-field"
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="label-eyebrow block mb-1.5">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="At least 8 characters"
            />
          </div>

          {error && <p className="text-sm text-severity-critical font-mono">{error}</p>}

          <button type="submit" disabled={busy} className="btn-primary w-full">
            {busy ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-center text-sm text-ink-muted mt-5">
          Already have an account?{" "}
          <Link to="/login" className="text-signal hover:text-signal-glow">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
