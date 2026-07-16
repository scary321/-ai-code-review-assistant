import useDocumentTitle from "../hooks/useDocumentTitle.js";
import { useEffect, useState } from "react";
import { api } from "../services/api.js";
import UploadPanel from "../components/UploadPanel.jsx";
import ProjectCard from "../components/ProjectCard.jsx";

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useDocumentTitle("Dashboard");

  useEffect(() => {
    api
      .listProjects()
      .then((res) => setProjects(res.projects))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <div className="mb-8">
        <div className="label-eyebrow mb-1">Dashboard</div>
        <h1 className="text-2xl font-semibold text-ink">Your submissions</h1>
        <p className="text-ink-muted text-sm mt-1">
          Upload a Python file or a zipped project to run static analysis, security
          scanning, complexity checks, and an AI review pass in one go.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-1">
          <UploadPanel onUploaded={(p) => setProjects((prev) => [p, ...prev])} />
        </div>

        <div className="md:col-span-2 space-y-3">
          {loading && <p className="text-ink-muted text-sm font-mono">Loading…</p>}
          {error && <p className="text-severity-critical text-sm font-mono">{error}</p>}
          {!loading && projects.length === 0 && (
            <div className="card p-8 text-center text-ink-muted text-sm">
              Nothing here yet. Submit a file to get your first review.
            </div>
          )}
          {projects.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      </div>
    </div>
  );
}
