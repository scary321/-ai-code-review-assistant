/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        base: {
          DEFAULT: "#14101f",
          panel: "#1c1730",
          raised: "#251f3d",
          border: "#362f52",
        },
        ink: {
          DEFAULT: "#ede9f7",
          muted: "#a99fc7",
          faint: "#6f6690",
        },
        signal: {
          DEFAULT: "#8b5cf6",
          dim: "#7c3aed",
          glow: "#a78bfa",
        },
        severity: {
          critical: "#f87171",
          high: "#fb923c",
          medium: "#facc15",
          low: "#60a5fa",
          info: "#9ca3af",
        },
      },
      fontFamily: {
        mono: ["'JetBrains Mono'", "ui-monospace", "monospace"],
        sans: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(139,92,246,0.25), 0 0 24px rgba(139,92,246,0.12)",
      },
    },
  },
  plugins: [],
};