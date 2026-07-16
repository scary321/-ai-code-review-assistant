import useDocumentTitle from "../hooks/useDocumentTitle.js";
import { useEffect, useState, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../services/api.js";
import ScoreGauge from "../components/ScoreGauge.jsx";
import FindingRow from "../components/FindingRow.jsx";
import ReactMarkdown from "react-markdown";

export default function ProjectDetail() {
  const { projectId } = useParams();
  const [reviews, setReviews] = useState([]);
  const [activeReview, setActiveReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  useDocumentTitle(activeReview ? `Project #${projectId} review` : `Project #${projectId}`);

  const loadReviews = useCallback(async () => {
    const res = await api.listReviews(projectId);
    setReviews(res.reviews);
    if (res.reviews.length > 0) {
      const detail = await api.reviewDetail(res.reviews[0].id);
      setActiveReview(detail.review);
    }
  }, [projectId]);

  useEffect(() => {
    setLoading(true);
    loadReviews()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [loadReviews]);

  async function handleRunReview() {
    setRunning(true);
    setError("");
    try {
      const res = await api.runReview(projectId);
      await loadReviews();
      setActiveReview((prev) => ({ ...res.review }));
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

async function handleDownload() {
  if (!activeReview) return;
  setGenerating(true);
  try {
    await api.generateReport(activeReview.id);
    const blob = await api.downloadReportBlob(activeReview.id);
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `review_${activeReview.id}_report.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    setError(err.message);
  } finally {
    setGenerating(false);
  }
}

  const breakdown = activeReview
    ? computeBreakdown(activeReview.findings)
    : {};

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <Link to="/" className="font-mono text-xs text-ink-muted hover:text-signal">
        ← back to dashboard
      </Link>

      <div className="mt-4 mb-6 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold text-ink">Project #{projectId}</h1>
        <div className="flex gap-2">
          <button onClick={handleRunReview} disabled={running} className="btn-primary">
            {running ? "Running review…" : activeReview ? "Run new review" : "Run first review"}
          </button>
          {activeReview && (
            <button onClick={handleDownload} disabled={generating} className="btn-secondary">
              {generating ? "Preparing…" : "Download PDF"}
            </button>
          )}
        </div>
      </div>

      {error && <p className="text-severity-critical text-sm font-mono mb-4">{error}</p>}
      {loading && <p className="text-ink-muted text-sm font-mono">Loading…</p>}

      {!loading && !activeReview && (
        <div className="card p-8 text-center text-ink-muted text-sm">
          No reviews yet for this project. Run one to see static analysis, security,
          complexity, and AI-driven findings.
        </div>
      )}

      {activeReview && (
        <div className="space-y-6">
          <ScoreGauge score={activeReview.review_score} breakdown={breakdown} />

          {activeReview.summary && (
            <div className="card p-5">
              <div className="label-eyebrow mb-2">Summary</div>
              <div className="text-sm text-ink prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{activeReview.summary}</ReactMarkdown>
              </div>
            </div>
          )}

          <div className="card overflow-hidden">
            <div className="label-eyebrow px-4 py-3 border-b border-base-border">
              Findings ({activeReview.findings.length})
            </div>
            {activeReview.findings.length === 0 ? (
              <div className="p-6 text-center text-ink-muted text-sm">
                No issues found. Clean pass.
              </div>
            ) : (
              activeReview.findings
                .slice()
                .sort((a, b) => severityRank(a.severity) - severityRank(b.severity))
                .map((f) => <FindingRow key={f.id} finding={f} />)
            )}
          </div>

          {reviews.length > 1 && (
            <div className="card p-4">
              <div className="label-eyebrow mb-3">Review history</div>
              <div className="flex flex-wrap gap-2">
                {reviews.map((r) => (
                  <button
                    key={r.id}
                    onClick={async () => {
                      const detail = await api.reviewDetail(r.id);
                      setActiveReview(detail.review);
                    }}
                    className={`font-mono text-xs px-3 py-1.5 rounded-md border ${
                      activeReview.id === r.id
                        ? "border-signal text-signal"
                        : "border-base-border text-ink-muted hover:border-signal-dim"
                    }`}
                  >
                    #{r.id} · {r.review_score}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function severityRank(sev) {
  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  return order[sev] ?? 5;
}

function computeBreakdown(findings) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
  findings.forEach((f) => {
    if (counts[f.severity] !== undefined) counts[f.severity] += 1;
  });
  return counts;
}
