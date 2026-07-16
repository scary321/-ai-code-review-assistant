const ORDER = ["critical", "high", "medium", "low", "info"];

const LABELS = {
  critical: "CRIT",
  high: "HIGH",
  medium: "MED",
  low: "LOW",
  info: "INFO",
};

function scoreColor(score) {
  if (score >= 85) return "text-severity-low";
  if (score >= 65) return "text-signal";
  if (score >= 40) return "text-severity-medium";
  return "text-severity-critical";
}

export default function ScoreGauge({ score, breakdown = {} }) {
  const total = ORDER.reduce((sum, k) => sum + (breakdown[k] || 0), 0);
  const colorClass = scoreColor(score);

  return (
    <div className="card p-6 flex flex-col md:flex-row md:items-center gap-6">
      <div className="flex items-baseline gap-2 shrink-0">
        <span className="font-mono text-ink-faint text-3xl">[</span>
        <span className={`font-mono text-6xl font-bold tabular-nums ${colorClass}`} style={{ textShadow: "0 0 24px currentColor" }}>
          {score.toFixed(0).padStart(2, "0")}
        </span>
        <span className="font-mono text-ink-faint text-2xl self-start mt-1">/100</span>
        <span className="font-mono text-ink-faint text-3xl">]</span>
      </div>

      <div className="flex-1 min-w-0">
        <div className="label-eyebrow mb-2">Finding spectrum — {total} total</div>
        <div className="flex h-3 w-full overflow-hidden rounded-full bg-base border border-base-border">
          {total === 0 ? (
            <div className="w-full bg-severity-low/30" />
          ) : (
            ORDER.map((key) =>
              breakdown[key] ? (
                <div
                  key={key}
                  className={`h-full`}
                  style={{
                    width: `${(breakdown[key] / total) * 100}%`,
                    backgroundColor: `var(--sev-${key})`,
                  }}
                  title={`${LABELS[key]}: ${breakdown[key]}`}
                />
              ) : null
            )
          )}
        </div>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1">
          {ORDER.map((key) => (
            <div key={key} className="flex items-center gap-1.5 font-mono text-xs text-ink-muted">
              <span
                className="inline-block h-2 w-2 rounded-sm"
                style={{ backgroundColor: `var(--sev-${key})` }}
              />
              {LABELS[key]} {breakdown[key] || 0}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
