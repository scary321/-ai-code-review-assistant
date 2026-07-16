import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="border-b border-base-border bg-base-panel/60 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="font-mono text-signal text-lg">&gt;_</span>
          <span className="font-mono font-semibold tracking-tight text-ink">codestand</span>
        </Link>

        {user && (
          <div className="flex items-center gap-4">
            <span className="font-mono text-xs text-ink-muted hidden sm:inline">{user.name}</span>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              className="btn-secondary !py-1.5 !px-3 text-xs"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
