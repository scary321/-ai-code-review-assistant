import { Navigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";

export default function ProtectedRoute({ children }) {
  const { user, ready } = useAuth();

  if (!ready) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <span className="font-mono text-ink-muted text-sm animate-pulse">loading…</span>
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;
  return children;
}
