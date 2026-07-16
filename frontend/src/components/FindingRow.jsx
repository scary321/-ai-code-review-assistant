const SEVERITY_STYLE = {
  critical: { bar: "bg-severity-critical", text: "text-severity-critical", label: "CRIT" },
  high: { bar: "bg-severity-high", text: "text-severity-high", label: "HIGH" },
  medium: { bar: "bg-severity-medium", text: "text-severity-medium", label: "MED" },
  low: { bar: "bg-severity-low", text: "text-severity-low", label: "LOW" },
  info: { bar: "bg-severity-info", text: "text-severity-info", label: "INFO" },
};

const SOURCE_LABEL = {
  pylint: "pylint",
  bandit: "bandit",
  radon: "radon",
  openai: "AI review",
};

export default function FindingRow({ finding }) {
  const style = SEVERITY_STYLE[finding.severity] || SEVERITY_STYLE.info;

  return (
    <div className="group flex border-b border-base-border last:border-b-0">
      <div className={`w-1.5 shrink-0 ${style.bar}`} />
      <div className="flex-1 min-w-0 px-4 py-3 grid grid-cols-[auto_1fr] gap-x-3">
        <span className="font-mono text-xs text-ink-faint pt-0.5 select-none">
          {finding.file_name || "—"}
          {finding.line_number ? `:${finding.line_number}` : ""}
        </span>
        <span className={`font-mono text-[10px] font-semibold uppercase tracking-wider ${style.text} justify-self-end`}>
          {style.label} · {SOURCE_LABEL[finding.source] || finding.source}
        </span>

        <span className="col-span-2 font-medium text-sm text-ink mt-1">{finding.issue}</span>

        {finding.explanation && (
          <span className="col-span-2 text-sm text-ink-muted mt-1">{finding.explanation}</span>
        )}

        {finding.suggestion && (
          <span className="col-span-2 text-sm text-signal-glow/90 mt-1.5 flex gap-1.5">
            <span className="font-mono text-ink-faint">→</span>
            {finding.suggestion}
          </span>
        )}
      </div>
    </div>
  );
}
