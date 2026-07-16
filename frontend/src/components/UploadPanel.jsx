import { useState, useRef } from "react";
import { api } from "../services/api.js";

export default function UploadPanel({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [projectName, setProjectName] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) {
      setError("Choose a .py or .zip file first.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const res = await api.uploadProject(file, projectName || file.name);
      setFile(null);
      setProjectName("");
      if (inputRef.current) inputRef.current.value = "";
      onUploaded(res.project);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card p-5 space-y-4">
      <div>
        <div className="label-eyebrow mb-2">New submission</div>
        <input
          type="text"
          placeholder="Project name (optional)"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          className="input-field"
        />
      </div>

      <label className="flex items-center justify-between gap-3 rounded-md border border-dashed border-base-border px-4 py-3 cursor-pointer hover:border-signal-dim transition-colors">
        <span className="font-mono text-sm text-ink-muted truncate">
          {file ? file.name : "Select .py or .zip"}
        </span>
        <span className="btn-secondary !py-1 !px-3 text-xs shrink-0">Browse</span>
        <input
          ref={inputRef}
          type="file"
          accept=".py,.zip"
          className="hidden"
          onChange={(e) => setFile(e.target.files[0] || null)}
        />
      </label>

      {error && <p className="text-sm text-severity-critical font-mono">{error}</p>}

      <button type="submit" disabled={busy} className="btn-primary w-full">
        {busy ? "Uploading…" : "Submit for review"}
      </button>
    </form>
  );
}
