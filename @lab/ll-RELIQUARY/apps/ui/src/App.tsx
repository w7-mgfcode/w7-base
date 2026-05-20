/*
 * Boilerplate landing — placeholder ONLY.
 *
 * This file gets rewritten by the first `stitch-design` run that produces S01.
 * Per .claude/rules/ui-design-pipeline.md, no hand-rolled UI past this stub.
 */

import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8282";
const TITLE = import.meta.env.VITE_GAME_TITLE ?? "Reliquary";

type Health = { status: string; service: string; phase: string };

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setHealth)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : String(e)),
      );
  }, []);

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <section className="max-w-xl text-center space-y-6">
        <h1
          className="text-5xl"
          style={{ fontFamily: "var(--font-display)", color: "var(--color-accent)" }}
        >
          {TITLE}
        </h1>
        <p style={{ color: "var(--color-ink-muted)" }}>
          Your shelf is empty. <br />
          The first relic awaits — but not in this boilerplate.
        </p>

        <div className="mt-10 text-sm font-mono">
          <div>API: {API_BASE}</div>
          {health && (
            <div style={{ color: "var(--color-accent)" }}>
              ✓ {health.service} — {health.status} ({health.phase})
            </div>
          )}
          {error && (
            <div style={{ color: "#e36b6b" }}>
              ✗ API unreachable: {error}
            </div>
          )}
        </div>

        <footer className="text-xs opacity-60 mt-12">
          Boilerplate phase. Next: run <code>Skill: stitch-design</code> against{" "}
          <code>STORYBOARD.md §5.S01</code>.
        </footer>
      </section>
    </main>
  );
}
