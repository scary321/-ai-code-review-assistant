import { Link } from "react-router-dom";

export default function ProjectCard({ project }) {
  const date = new Date(project.created_at);

  return (
    <Link
      to={`/projects/${project.id}`}
      className="card p-4 flex items-center justify-between group hover:border-signal-dim transition-colors"
    >
      <div className="min-w-0">
        <div className="font-medium text-ink truncate">{project.project_name}</div>
        <div className="font-mono text-xs text-ink-muted mt-1">
          {project.upload_type === "zip" ? "archive" : "single file"} · uploaded{" "}
          {date.toLocaleDateString()}
        </div>
      </div>
      <span className="font-mono text-signal opacity-0 group-hover:opacity-100 transition-opacity">
        →
      </span>
    </Link>
  );
}
